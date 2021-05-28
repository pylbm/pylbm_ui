import numpy as np
import matplotlib.pyplot as plt

gamma = 1.4


def f_alpha_old(alpha, theta, rho_in, ux_in, p_in):
    st = np.sin(theta)
    ca = np.cos(alpha)
    ta = np.tan(alpha)
    cda = ca*ca
    samt = np.sin(alpha-theta)
    cdamt = np.cos(alpha-theta)**2
    tamt = np.tan(alpha-theta)
    return rho_in*ux_in**2*(
        .5*(cdamt - cda) - gamma/(gamma-1)*ca*st*samt
    ) / cdamt - gamma/(gamma-1)*p_in*(
        tamt - ta
    ) / ta


def f_alpha(alpha, theta, Ma_in):
    st = np.sin(theta)
    ca = np.cos(alpha)
    ta = np.tan(alpha)
    cda = ca*ca
    samt = np.sin(alpha-theta)
    cdamt = np.cos(alpha-theta)**2
    tamt = np.tan(alpha-theta)
    return Ma_in**2*(
        .5*(cdamt - cda) - gamma/(gamma-1)*ca*st*samt
    ) / cdamt - 1/(gamma-1)*(
        tamt - ta
    ) / ta


def dichotomie(f, a, b, epsilon=1.e-10):
    fa, fb = f(a), f(b)
    c = .5*(a+b)
    fc = f(c)
    if fa*fb > 0:
        print("Problem in dichotomie")
        return
    while b - a > epsilon:
        if fa*fc >= 0:
            a, fa = c, fc
        if fb*fc >= 0:
            b, fb = c, fc
        c = .5*(a+b)
        fc = f(c)
    return c


def wedge(theta, Ma_in):
    alpha = dichotomie(
        lambda x: f_alpha(x, theta, Ma_in),
        theta, 1.2
    )
    Ma_out2 = np.sin(2*alpha) / np.sin(2*alpha-2*theta) / (
        1/Ma_in**2 + gamma * np.sin(alpha) * np.sin(theta) / np.cos(alpha-theta)
    )
    return alpha, np.sqrt(Ma_out2)


if __name__ == "__main__":
    theta = 15 * np.pi/180
    mach_in = np.linspace(2, 9, 40)
    mach_out = np.zeros(mach_in.shape)
    alpha = np.zeros(mach_in.shape)

    for k, Ma_in in enumerate(mach_in):
        alpha[k], mach_out[k] = wedge(theta, Ma_in)

    fig = plt.figure(figsize=(6, 6))

    axM = fig.add_subplot(1, 1, 1)
    axM.set_title(r"Wedge for $\theta=15^\circ$")
    axM.plot(mach_in, mach_out, color='navy', linewidth=2)
    axM.set_xlabel("Mach inlet")
    axM.set_ylabel("Mach outlet", color='navy')
    axM.tick_params(axis='y', labelcolor='navy')
    axM.grid(True, color='navy', alpha=0.5, linestyle='dotted')

    axa = axM.twinx()
    axa.plot(mach_in, alpha*180/np.pi, color='orange', linewidth=2)
    axa.set_ylabel(r"$\beta$ (degree)", color='orange')
    axa.tick_params(axis='y', labelcolor='orange')
    axa.grid(True, color='orange', alpha=0.5, linestyle='dotted')

    fig.savefig("wedge_theta_15.png")
