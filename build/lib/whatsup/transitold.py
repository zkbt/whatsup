from zachopy.Talker import Talker
buffer = 1.0
class Transit(Talker):
    def __init__(self, planet, i, phasefrommidtransit=0.0):
        Talker.__init__(self)
        self.planet = planet
        self.midtransit = planet.period*(i + phasefrommidtransit) + planet.transit_epoch
        self.i = i

    @property
    def duration(self):
        return self.planet.duration

    @property
    def pretransit(self):
        return self.midtransit - self.duration*(0.5 + buffer)

    @property
    def pretransit(self):
        return self.midtransit + self.duration*(0.5 + buffer)

    def plot(self, ax=None, y=0, alpha=0.5, linewidth=5, **kwargs):
        ax.plot([self.pretransit, self.postransit], [y,y], color=self.planet.color, **kwargs)
