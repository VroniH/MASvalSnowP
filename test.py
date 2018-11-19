import salem
import motionless
import matplotlib.pyplot as plt

# g = salem.GoogleVisibleMap(x=[14.,16.],y=[77.5,79],size_x=200,size_y=200)
# sm = salem.Map(g.grid, factor=1, countries=False)
# sm.set_rgb(g.get_vardata())
# f, ax = plt.subplots(1, 1, figsize=(8, 8))
# sm.visualize(ax=ax)



h = salem.GoogleCenterMap(center_ll=(15.625305,78.216102),
size_x=400,size_y=400, maptype='terrain')
sm = salem.Map(h.grid, factor=1, countries=False)
sm.set_rgb(h.get_vardata())
f, ax = plt.subplots(1, 1, figsize=(8, 8))
sm.visualize(ax=ax)
plt.show()
