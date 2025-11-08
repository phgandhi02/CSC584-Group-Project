# README
This repository contains the source code for my CSC584 Building Game AI project. The project objective is to create a rogue-like game that uses procedural content generation (PCG) techniques to generate levels. The PCG requires parameters that need to be tuned for achieving a certain look. The parameters can be tuned using a LLM that will take information from the user and generate the appropriate parameter weights accordingly. 

## Setup LLM

- Using Docker:
To set up the LLM, you can use the following Docker command to run the Ollama LLM server with GPU support:
```bash
docker run --gpus=all -d -v ollama:/root/.ollama -p 11434:11434 --name LLM ollama/ollama
```
Then start the model by entering the container (make sure the container is running, otherwise start it with `docker start LLM`):
```bash
docker exec -it LLM bash
ollama run <model-name>
```
- Local Installation:
Ollama can be locally installed by downloading and installing the Ollama application from [here](https://ollama.com/download). Then, start the ollama server and run the model (it will also download the model if not on the machine already) by using the following command:
```bash
ollama run <model-name>
```

The project uses port 11434 by default to connect to the LLM server. Make sure that the port is open and accessible. This port may be occupied by other apps such as Docker containers, so ensure that there are no conflicts.

## Relevant Repos
- https://github.com/1allan/tower-of-bullets
- https://github.com/VictorHachard/pygame-roguelike
- https://github.com/sandromund/pygame_roguelike

## Tutorials:
- https://www.roguebasin.com/index.php/Complete_Roguelike_Tutorial,_using_python%2Blibtcod,_part_1
- https://pygame-dev.blogspot.com/
- [Cellular Automata Method for Generating Random Cave-Like Levels](https://www.roguebasin.com/index.php?title=Cellular_Automata_Method_for_Generating_Random_Cave-Like_Levels)
- [Code design basics](https://roguebasin.com/index.php/Code_design_basics)

## Relevant Articles
- https://slsdo.github.io/procedural-dungeon/
- http://pcg.wikidot.com/pcg-algorithm:dungeon-generation (many resources in here)
