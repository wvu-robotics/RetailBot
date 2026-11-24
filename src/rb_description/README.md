# rb_description
## Onshape Export
https://onshape-to-robot.readthedocs.io/en/latest/
Using the onhape to URDF exporter gives us a ready to use URDF with good naming
and inertia properties that we can quickly update. There is some setup required.

The package to do this is `onshape-to-robot` and is available as PyPi package.
It requires a few dependencies: `numpy pybullet requests commentjson colorama
numpy-stl`.

Installation and API key setup instructions can be found here: https://onshape-to-robot.readthedocs.io/en/latest/installation.html

**Note**. Don't add your API key to the config.json as this will give someone
the same access to your OnShape account as if they were logged in as you!
Instead manually set the ENV variables or have a script to set them outside of
the repo.

`// Obtained at https://dev-portal.onshape.com/keys
export ONSHAPE_API=https://cad.onshape.com
export ONSHAPE_ACCESS_KEY=Your_Access_Key
export ONSHAPE_SECRET_KEY=Your_Secret_Key`

`openscad` and `meshlab` are optional deps.
