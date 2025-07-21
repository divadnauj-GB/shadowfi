# shadowfi
SHADOWFI is an open source fault injection framework that leverages hyperscale computing to speed up the fault evalaution tasks. 

## Getting Statarted with Shadowfi

### Prerequisites
- 


### local instalation 

#### Install OSS CAD SUITE
-


## local instalation


## Build your singularity container

Clone oss-cad-suite into the `sif` directory

```
cd sif
# download the oss-cad suit 20241117 release 
wget https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-11-17/oss-cad-suite-linux-x64-20241117.tgz
# uncompress into the current directory
tar -xvzf oss-cad-suite-linux-x64-20241117.tgz
# create the singularity image 
sudo singularity build oss-cad-container.sif oss-cad-container.def
```



