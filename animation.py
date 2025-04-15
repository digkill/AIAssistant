from direct.showbase.ShowBase import ShowBase
from panda3d.core import Point3

class Assistant3D(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.model = self.loader.loadModel("models/assistant_guffy_girl.obj")
        self.model.reparentTo(self.render)
        self.model.setScale(1.5)
        self.model.setPos(0, 10, 0)

        self.taskMgr.add(self.rotate_model, "RotateTask")

    def rotate_model(self, task):
        angle = task.time * 30
        self.model.setH(angle)
        return task.cont

app = Assistant3D()
app.run()