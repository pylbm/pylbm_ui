> [_From Wikipedia, the free encyclopedia_ ](https://en.wikipedia.org/wiki/Acoustics)
>
> Acoustics is a branch of physics that deals with the study of mechanical waves in gases, liquids, and solids including topics such as vibration, sound, ultrasound and infrasound. A scientist who works in the field of acoustics is an acoustician while someone working in the field of acoustics technology may be called an acoustical engineer. The application of acoustics is present in almost all aspects of modern society with the most obvious being the audio and noise control industries.
>
> Hearing is one of the most crucial means of survival in the animal world and speech is one of the most distinctive characteristics of human development and culture. Accordingly, the science of acoustics spreads across many facets of human society—music, medicine, architecture, industrial production, warfare and more. Likewise, animal species such as songbirds and frogs use sound and hearing as a key element of mating rituals or marking territories. Art, craft, science and technology have provoked one another to advance the whole, as in many other fields of knowledge. Robert Bruce Lindsay's "Wheel of Acoustics" is a well accepted overview of the various fields in acoustics.

The acoustics system in dimension 1 is
the simplest model of linear hyperbolic system.

Denoting $c$ a real constant, the scalar quantities $\rho(t, x)$ and $q(t, x)$,
where $t$ is the time and $x$ the one-dimensional space variable,
satisfy the acoustics system

$$
    \left\lbrace\begin{aligned}
    &\partial_t \rho(t,x) + \partial_x q(t,x) = 0,&& t>0, \ x\in\mathbb{R},\\
    &\partial_t q(t,x) + c^2 \partial_x \rho(t,x) = 0,&& t>0, \ x\in\mathbb{R},\\
    &\rho(0,x) = \rho_0(x), && x\in\mathbb{R},\\
    &q(0,x) = q_0(x), && x\in\mathbb{R},
    \end{aligned}\right.
$$

where $\rho_0$ and $q_0$ are given functions (the initial configuration).

The solution of the acoustics system is given by

$$ \begin{aligned}
\rho(t, x) 
&= \frac{\rho_0(x-ct)+\rho_0(x+ct)}{2}
+ \frac{q_0(x-ct)-q_0(x+ct)}{2c},\\
q(t, x)
&= c\frac{\rho_0(x-ct)-\rho_0(x+ct)}{2}
+ \frac{q_0(x-ct)+q_0(x+ct)}{2}.
\end{aligned}
$$