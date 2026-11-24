# Retail Bot

This repo is intended to be used on a real robot, personal computer, or on a remote server (i.e. simulation).

# How to Get This Repo

```
git clone --recursive git@github.com:wvu-robotics/retail-bot.git
```

Since this repo uses submodules it is recommend to also clone those using the `--recursive` flag above. If the repo is cloned without the recursive subcommand you can clone the submodules later by running `git submodule update --init --recursive`.

To examine the installed submodules use `git submodules`.

# Dependencies

For guidance please refer to the installation instructions for these projects.

**REQUIRED:**

- [docker engine](https://docs.docker.com/engine/install/)
- docker-compose
- docker buildx

**OPTIONAL:**

- [Nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- [devpod](https://devpod.sh/docs/getting-started/install)

# Development Workflow

## Working Inside a Container

It is preferred to edit/run/debug in a container as the dependencies for a ROS2 project are quite heavy and OS specific. Working in a container also gives a stronger guarantee your code will run on another machine/robot. There are a few recommend methods to do this:

- VSCodium remote
- Docker interactive shell

<details><summary>Other Options:</summary>
There is a VSCode containers extension that may work but is intentionally broken by microsoft to work only with their build of VSCode.
</details>

## Code Style and Formatting

This project follows the ROS2 st

## SSH Forwarding

Creating an SSH key on the host machine and forwarding the host machine SSH agent to the container lets you easily and securely pull/push from the remote repo without having to switch to the host machine.

<!-- TODO -->

Make an SSH key:

```
ssh-keygen
```

## How to Use the Workspace Container

All container related files are in the directory `.devcontainer`.
This workspace includes a container specification file (Dockerfile) which is
built into a docker image and ran as a container. This can be done using
either manual `docker` commands, `devpod` commands, or with other devcontainer
compatible tools like VSCode.

**The recommended way to build/run the workspace container is with devpod**.
Devpod can then be used to launch and attach VSCode to a running container.
Devpod can be obtained as a standalone AppImage executable for Linux. Devpod
will read a devcontainer.json file and use this to find, build, and run a
Dockerfile.
The Image is specified in the Dockerfile but buildtime and runtime behaviours
are specified in a devcontainer.json.

Devpod installation and dependencies instructions can be found here:
https://devpod.sh/docs/getting-started/install

## Building the Image

To build the docker image use the command `make dockerbuild` in the top level of
the repo where the Makefile resides. This will take a long time for the initial
build but will be much quicker thereafter.

### Docker Dependencies

Install the following APT packages.

- docker
- docker-compose
- docker-buildx

Enable the docker daemon and add your user to the docker group
`usermod -aG docker <your_username>`. Be warned the image and the container use
poor security practice (including use of the --privileged flag). TODO fix
this...

It is recommended ot install [the](the) nvidia docker toolkit as well. Thi

## Running the Container

To run without GPU support `./qrun`

To run with GPU support `./qrun -g`

To restart a container add the `-r` flag. E.g. `./qrun -r` will restart a
non-GPU container.

### X Forwarding

Allow the local X server to accept remote connections

`xhost +local:`

This is somewhat insecure...

# Misc

## Creating an SSH Key

This allows for much easier login to any remote host over SSH. An SSH key is also necessary to interact with private remote repos like the ones GitHub hosts. It is recommended to name the SSH key and to secure it with a memorable password.

```bash
ssh-keygen
```

## Using an SSH Agent

Using an SSH agent allows you to "unlock" an ssh key for a set amount time which enables password-less logins to remote hosts.

First we make sure the SSH agent daemon process is always running:

Then make it so that the ssh-agent will automatically ask us to unlock keys and will keep them unlocked in the keyring for a set time.

## Setting up an SSH .config

Doing this enables you to more easily connect to a remote host with a simple command like:

```bash
ssh nickname
```

Add an entry to `~/.ssh/config` like the following example:

```
Host <nickname>>
	HostName <192.xxx.xxx.xxx>
	SetEnv TERM=xterm
	User <user_name>
	IdentitiesOnly yes
	IdentityFile ~/.ssh/<your_ssh_private_key>
```

## Disable Docker from pausing with CTRL-P

This is usually the keymap for "previous" on a command buffer. Docker has a very strange default binding that _pauses_ the container. We can disable this by adding the following to `~/.docker/config.json` on our host machine.

```json
{
  "detachKeys": "ctrl-e,e"
}
```

# Troubleshooting
Two containers running on the same host can not communicate over ros2 topics. This is maybe due to them trying to use shared memory and failing. Force them to use UDP4 and communciate over the loopback connection.

```bash
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4
```
