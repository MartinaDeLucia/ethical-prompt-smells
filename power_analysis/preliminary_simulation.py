import numpy as np, sys, json, itertools, time
from scipy.optimize import minimize
from scipy.special import expit
from multiprocessing import Pool

ALPHA = np.array([-1.5, -0.5, 0.5, 1.5])   # baseline thresholds (5 categories)
L, R = 3, 3
SD_U, SD_V = 1.0, 0.7                     # prompt, prompt x LLM
GAMMA = np.array([0.0, 0.3, -0.3])         # LLM effects

def simulate(P, beta, tau, rng):
    u = rng.normal(0, SD_U, P); b = rng.normal(0, tau, P)
    v = rng.normal(0, SD_V, (P, L))
    rows = []
    for p in range(P):
        for l in range(L):
            for c in (0, 1):
                for r in range(R):
                    eta = beta*c + GAMMA[l] + u[p] + v[p, l] + b[p]*c
                    ystar = eta + rng.logistic()
                    y = int(np.searchsorted(ALPHA, ystar))  # 0..4
                    rows.append((p, l, c, y))
    return np.array(rows)

def fit(data, P):
    p_, l_, c_, y = data.T
    n = len(y)
    # design for eta: cond, LLM2, LLM3, prompt dummies 2..P
    X = np.zeros((n, 3 + P - 1))
    X[:, 0] = c_
    X[l_ == 1, 1] = 1; X[l_ == 2, 2] = 1
    for k in range(1, P):
        X[p_ == k, 2 + k] = 1
    K = 4
    def unpack(th):
        a = np.cumsum(np.concatenate([[th[0]], np.exp(th[1:K])]))
        return a, th[K:]
    def ll_and_scores(th, need_scores=False):
        a, bb = unpack(th)
        eta = X @ bb
        aext = np.concatenate([[-np.inf], a, [np.inf]])
        up = aext[y + 1] - eta; lo = aext[y] - eta
        Fu = expit(up); Fl = expit(lo)
        D = np.clip(Fu - Fl, 1e-12, None)
        fu = Fu*(1-Fu); fl = Fl*(1-Fl)
        ll = np.log(D).sum()
        # d ll / d eta
        s_eta = -(fu - fl)/D
        # d ll / d alpha_j
        S_a = np.zeros((n, K))
        idx = np.arange(n)
        mu = y < K; S_a[idx[mu], y[mu]] += fu[mu]/D[mu]
        ml = y > 0; S_a[idx[ml], y[ml]-1] -= fl[ml]/D[ml]
        # chain to theta
        J = np.zeros((K, K)); J[:, 0] = 1
        for k in range(1, K): J[k:, k] = np.exp(th[k])
        S_th = S_a @ J
        S = np.hstack([S_th, s_eta[:, None]*X])
        return ll, S
    def obj(th):
        ll, S = ll_and_scores(th)
        return -ll, -S.sum(0)
    th0 = np.concatenate([[ -1.5], np.zeros(K-1), np.zeros(X.shape[1])])
    res = minimize(obj, th0, jac=True, method='L-BFGS-B', options={'maxiter': 2000})
    ll, S = ll_and_scores(res.x)
    B = S.T @ S                           # OPG bread
    Binv = np.linalg.pinv(B)
    G = np.zeros((P, S.shape[1]))
    np.add.at(G, p_, S)
    M = G.T @ G
    V = Binv @ M @ Binv
    j = K  # cond coefficient index
    return res.x[j], np.sqrt(max(V[j, j], 1e-12))

def one(args):
    P, beta, tau, seed = args
    rng = np.random.default_rng(seed)
    d = simulate(P, beta, tau, rng)
    est, se = fit(d, P)
    return est - 1.96*se   # lower bound of two-sided 95% CI

if __name__ == '__main__':
    reps = int(sys.argv[1])
    Ps = [20, 40, 60]
    scen = []
    for tau in (0.0, 0.5):
        for name, beta, thr in [('EA_OR1.5', np.log(1.5), 0.0), ('EA_OR2', np.log(2.0), 0.0),
                                ('RF_OR1_vs_2/3', 0.0, np.log(2/3)), ('RF_OR0.9_vs_2/3', np.log(0.9), np.log(2/3))]:
            for P in Ps:
                scen.append((name, tau, P, beta, thr))
    out = {}
    t = time.time()
    with Pool() as pool:
        for name, tau, P, beta, thr in scen:
            lbs = pool.map(one, [(P, beta, tau, 1000*P + s + int(tau*1e6) + hash(name) % 9999) for s in range(reps)])
            pw = float(np.mean(np.array(lbs) > thr))
            out[f'{name}|tau={tau}|P={P}'] = pw
            print(name, tau, P, round(pw, 3), round(time.time()-t), flush=True)
    json.dump(out, open('results.json', 'w'), indent=1)
