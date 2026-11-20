from __future__ import annotations

import numpy as np
from ase import Atoms

from mcp_atomictoolkit.md_runner import _initialize_velocities, _select_integrator


def make_atoms() -> Atoms:
    return Atoms(
        "Ar4",
        positions=[
            [0.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
            [0.0, 0.0, 2.0],
        ],
        cell=[10.0, 10.0, 10.0],
        pbc=True,
    )


def test_maxwell_boltzmann_velocity_initialization_is_reproducible() -> None:
    first = make_atoms()
    second = make_atoms()
    _initialize_velocities(first, 300.0, rng=np.random.RandomState(20261120))
    _initialize_velocities(second, 300.0, rng=np.random.RandomState(20261120))
    assert np.allclose(first.get_momenta(), second.get_momenta(), rtol=0.0, atol=1e-14)


def test_maxwell_boltzmann_velocity_initialization_changes_with_seed() -> None:
    first = make_atoms()
    second = make_atoms()
    _initialize_velocities(first, 300.0, rng=np.random.RandomState(17))
    _initialize_velocities(second, 300.0, rng=np.random.RandomState(18))
    assert not np.allclose(first.get_momenta(), second.get_momenta(), rtol=0.0, atol=1e-14)


def test_langevin_integrator_receives_seeded_rng() -> None:
    rng = np.random.RandomState(42)
    dynamics = _select_integrator(
        atoms=make_atoms(),
        integrator="langevin",
        timestep_fs=1.0,
        temperature_K=300.0,
        friction=0.02,
        taut=100.0,
        rng=rng,
    )
    assert dynamics.rng is rng
