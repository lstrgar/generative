Hyphae is an algorithm that operates on points in the 2 dimensional plane. Beginning with a pre-defined number of seed nodes, we randomly select an existing node and attempt to "grow" from this point, by adding a new node and painting a connection between the original point and the new point. The only really meaningful stipulation being that connecting lines are not allowed to collide. Collisions are avoided by maintaining a zoning system on the canvas checking minimum distance between nodes that fall in the same or nearby zones. We also define a bounding shape, outside of which growth is not allowed. The bounding shape is represented as a spline curve, which is interpolated from a set of points provided by the user. If a set of points are not provided the bounding shape defaults to a circle with a diameter equal to the height, width of the canvas. 
 
There are a number of levers we can pull to modify the algorithms growth behavior and, ultimately, the drawn image. One can specify:

The number of source nodes
The source node radius
The maximum angle a new node can branch from their parent's direction
The maximum number of children a node can sprout
 
