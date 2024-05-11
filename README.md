# Universe Simulation Using Seed as Parameter Generator

## Project Goal:
The goal of this project is to create a simple universe simulator based on the use of a single seed as a generator for all parameters of the simulated environment. The inspiration for the project is the seed mechanism used in the game Minecraft, where entering a specific seed generates a unique game environment. In our case, the seed will be used to generate all parameters for simulated environments, such as ant life, population of organisms in the forest.

## Project Scope:
1. Implementation of the simulation in Python.
2. Use of a single seed as a parameter generator for the simulation.
3. Simulating ant behaviors on a board of a specified dimension, where they will move and interact with each other based on certain rules. (Inter-species combat, chance of queen birth, or available food)
4. Introducing various initial parameters of the simulation, such as the number of ants, their characteristics, or the probability of occurrence of various events, dependent on the seed value.
5. Collecting data from the simulation, such as the population count of ants in subsequent epochs of the simulation.
6. Saving the output data in a CSV file.
7. An additional element may be the ability to preview in real time through a web browser (working simulation in slow motion), which will allow observing the world on an ongoing basis.
8. The ability to compare results with other universes through seed values, which will allow for the analysis of differences between different environments.

Thanks to such an extensive simulation, students will be able to not only experiment with different seeds and parameters, but also observe the simulation in real time and compare results between different universes. This project will allow for the practical application of object-oriented programming techniques and will enable understanding of the basics of agent simulation. It is worth noting that all simulation parameters will be deterministically dependent on one seed value, which will allow for repeatability of simulation results.