class Recommendation:

    def __init__(self, sim_rec_list, demand_rec_list, total_avg, avg_by_dept, count_by_dept, high_demand, low_demand):

        self._sim_rec_list = sim_rec_list
        self._demand_rec_list = demand_rec_list
        self._total_avg = total_avg
        self._avg_by_dept = avg_by_dept
        self._count_by_dept = count_by_dept
        self._high_demand = high_demand
        self._low_demand = low_demand 

    def get_sim_recs(self):
        return self._sim_rec_list

    def get_demand_recs(self):
        return self._demand_rec_list
    
    def get_total_avg(self):
        return self._total_avg

    def get_avg_dept(self):
        return self._avg_by_dept

    def get_count_dept(self):
        return self._count_by_dept

    def get_high_demand(self):
        return self._high_demand

    def get_low_demand(self):
        return self._low_demand



        