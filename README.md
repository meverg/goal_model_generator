# Automated Release Model Generator

This project involves extracting requirements from user stories, establishing the parent-child relations among requirements, determining the AND/OR refinement types, and understanding other relations among requirements (temporal, conflict, contribution)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This project is written in `Python 3`, uses `pipenv` for package management and optionally uses `Docker` for production. So it is assumed that you have these requirements installed.
Also you should install [optimathsat](http://optimathsat.disi.unitn.it/pages/download-js.html) and copy it to the project directory with the name `optimathsat`. 

_Note that it has different distributions for different operating systems. So install the one for your operating system as `optimathsat` and one for the linux as `optimathsat_linux` if you are going to use `Docker`_

### Installing

- If you are going to use `Docker` to run the project you can use this command in the project directory and see it on `localhost:5000`:
```
docker run -p 5000:5000 -d goal-model-generator
```

- If you are going to run the project locally you can benefit from `pipenv`. In the project directory run these commands:

```
pipenv install
pipenv shell
flask run
```

## Deployment

If you want to deploy the app for yourself you can use `docker-machine` as I did to run the container on an `AWS EC2` instance. You can of course use a better tier but smaller (_free_) tier lacks the memory so ...
```
docker-machine create --driver amazonec2 --amazonec2-instance-type "t2.small"  --amazonec2-open-port 5000 goal-model-generator
```

## Authors

* [**Emin Vergili**](https://github.com/meverg)
* [**Didem Öngü**](https://tr.linkedin.com/in/didem-%C3%B6ng%C3%BC-a29918178)

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details

## Acknowledgments

We would like to express our very great appreciation to [Dr. Aydemir](https://www.cmpe.boun.edu.tr/people/basak.aydemir) for her valuable and constructive suggestions during the planning and development of this research work. Her willingness to give her time so generously has been very much appreciated.
