# Specialist Agent: DataHarvester

class AgentInstance:

    ROLE = "DataHarvester"

    MISSION = "Harvest web feeds"

    

    def run(self):

        return {"status": "ONLINE", "role": self.ROLE}

