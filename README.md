# cycsat
A synthetic satellite time series generator intended for use with Cyclus for nuclear non-proliferation monitoring.

## agent class
This is the core class of cycsat. Anything that can be observed in a satellite image is defined as an agent. An agent is defined by a geometry (Shapely geometry), a material response (see the material class), core attributes that are tracked over time, and a behavior (a user-defined _run function).

Agents can be assigned sub-agents. A sub-agent's geometry must fall within it's parent agent. Agents have rules that provide instructions for how to place sub-agents. Running or plotting an agent will run all its sub-agents.

## material class
This class defines how the surface of an agent is converted to numeric values for rendering a raster image. A built-in subclass called USGSMaterial uses the USGS Spectral Library to model the spectral response of a wide variety of materials (e.g. concrete, water, forest, metal. See the USGS Spectral Library for a complete list.). A USGSMaterial instance takes a wavelength value and returns a reflectance value. Users can define their own material subclasses.

## rule class
This class defines an instruction for an agent to place a particular sub-agent. Some pre-defined rules include NEAR (place a named sub-agent near to another named sub-agent) and ALIGN (align a named sub-agent by its x or y axis to another named sub-agent). Users can define their own rule subclasses.

## example

The example shown below demonstrates an RGB rendering of a simple reactor with two cooling towers. The white circle represents a plume. See sample.py to see how this was created.

![Alt text](/samples/site_render_example.png?raw=true "Optional Title")
