#!/usr/bin/env python3
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import pytest
import torch
import matplotlib.pyplot as plt

import curvetorch as curve


def basic(tensor):
    x, y = tensor
    return x * x + y * y


def rosenbrock(tensor):
    x, y = tensor
    return (1 - x) ** 2 + 1 * (y - x ** 2) ** 2


def quadratic(tensor):
    x, y = tensor
    a = 1.0
    b = 1.0
    return (x ** 2) / a + (y ** 2) / b


cases = [
    (basic, (-1.0, 0.5), (0, 0)),
    (rosenbrock, (1.5, 1.5), (1, 1)),
    (quadratic, (0.5, 0.5), (0, 0)),
]


def ids(v):
    n = '{} {}'.format(v[0].__name__, v[1:])
    return n


optimizers = [
    (curve.CurveSGD, {'lr': 0.0015}, 15000),
]


@pytest.mark.parametrize('case', cases, ids=ids)
@pytest.mark.parametrize('optimizer_config', optimizers, ids=ids)
def test_benchmark_function(case, optimizer_config):
    func, initial_state, min_loc = case
    optimizer_class, config, iterations = optimizer_config

    x = torch.Tensor(initial_state).requires_grad_(True)
    x_min = torch.Tensor(min_loc)
    optimizer = optimizer_class([x], **config)
    fs = []
    for _ in range(iterations):
        fs.append(func(x))
        def closure():
            optimizer.zero_grad()
            f = func(x)
            f.backward(retain_graph=True, create_graph=True)
            return f
        optimizer.step(closure)
    plt.plot(range(iterations), fs)
    plt.show()

    assert torch.allclose(x, x_min, atol=0.01)

    name = optimizer.__class__.__name__
    assert name in optimizer.__repr__()
