from Pyblio import Config

Config.define ("style/custom", """ Format of the custom output style """)

Config.set ("style/custom", "%(title)-35s %(author)-25s %(date)s")
