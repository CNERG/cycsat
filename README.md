# cycsat
A synthetic satellite time series generator intended for use with Cyclus for nuclear non-proliferation monitoring. cycsat is made up of agents, materials, and rules.

## Agents
This is the core class of cycsat. Anything that can be observed in a satellite image is an agent. An agent is defined by a geometry (a ![Shapely](https://pypi.python.org/pypi/Shapely) Polygon or Point object), a material response (see the material class), core attributes that are tracked over time, and a behavior (a user-defined _run function).

Agents can be assigned sub-agents. A sub-agent's geometry must fall within it's parent agent. Agents have rules that provide instructions for how to place sub-agents. Running or plotting an agent will run all its sub-agents. A hierarchical structure of agents and sub-agents is called an "agent tree."

## Materials
This class defines how the surface of an agent is converted to numeric values for rendering a raster image. A built-in subclass called USGSMaterial uses the USGS Spectral Library to model the spectral response of a wide variety of materials (e.g. concrete, water, forest, metal. See the USGS Spectral Library for a complete list.). A USGSMaterial instance takes a wavelength value and returns a reflectance value. Users can define their own material subclasses.

## Rules
This class defines an instruction for how an agent is to place one of its named sub-agents. Some pre-defined rules include NEAR (place a named sub-agent near to another named sub-agent) and ALIGN (align a named sub-agent by its x or y axis to another named sub-agent). Users can define their own rule subclasses.

## Example
The example shown below demonstrates a RGB rendering of a simple reactor with two cooling towers. The green background is lawn grass, the gray is concrete, the large circle is water, and the black shapes are black roof asphalt. The white circle (modeled using the spectral response of snow) represents a cooling tower plume. See sample.py to see how this agent stack.

![Alt text](/samples/site_render_example.png?raw=true "Optional Title")
