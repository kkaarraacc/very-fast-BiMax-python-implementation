import copy

class BiMax(object):

    def __init__(self, data):
        self.data = data
        self.processbiclusters = []
        self.databiclusters = []
        self.filtereddataclusters = []
        self.filteredprocessclusters = []

    def findBiclusters(self):
        if self.processbiclusters:    #exception for when the bimax process was already run
            print('Found ' + str(len(self.processbiclusters)) + ' biclusters')
            return
        self.processbiclusters = self.bimax(self.data, self.processbiclusters)
        print('Found ' + str(len(self.processbiclusters)) + ' biclusters')

    def getDataFormattedBiclusters(self):
        if not self.processbiclusters:   #exception for empty bicluster list
            print('Bicluster list is empty')
            return
        if self.databiclusters:       #exception for when translation was already performed
            return self.databiclusters
        self.databiclusters = copy.deepcopy(self.processbiclusters)  #makes a copy of the processbiclusters and rewrites all elements of the copy as data entries
        for i in range(len(self.databiclusters)):
            for j in range(len(self.databiclusters[i])):
                for k in range(len(self.databiclusters[i][j])):
                    if j == 0:
                        itemLocation = self.databiclusters[i][j][k]
                        self.databiclusters[i][j][k] = self.data[itemLocation][0]
                    else:
                        attrLocation = self.databiclusters[i][j][k]
                        self.databiclusters[i][j][k] = self.data[0][attrLocation]
        
    def filterBiclusters(self, minrows, mincolumns):
        self.filtereddataclusters = []
        self.filteredprocessclusters = []
        filtercount = 0
        if self.processbiclusters:
            for i in range(len(self.processbiclusters)):
                if len(self.processbiclusters[i][0]) >= minrows and len(self.processbiclusters[i][1]) >= mincolumns:
                    self.filteredprocessclusters.append(self.processbiclusters[i])
                    filtercount += 1
        if self.databiclusters:
            filtercount = 0
            for i in range(len(self.databiclusters)):
                if len(self.databiclusters[i][0]) >= minrows and len(self.databiclusters[i][1]) >= mincolumns:
                    self.filtereddataclusters.append(self.databiclusters[i])
                    filtercount += 1
        if not self.processbiclusters or not self.databiclusters:
            print("Bicluster lists are empty")
        else:
            print("Filtered out " + str(filtercount) + " " + str(minrows) + "x" + str(mincolumns) + " minimum biclusters")
        
    def bimax(self, data, processbiclusters):
        R = list(range(1, len(data)))
        C = list(range(1, len(data[0])))
        if BiMax.isCluster(data, R, C):
            processbiclusters.append([R]+[C])
            return processbiclusters
        UR, UC, VR, VC = BiMax.getUV(data, R, C)
        Z = (set(C) - set(UC))
        if len(UR) > 1:       #non-empty and non-singlewine row checks for U and V
            BiMax.bimaxU(data, UR, UC, processbiclusters)
        if len(VR) > 1:
            BiMax.bimaxV(data, VR, VC, processbiclusters, Z)   
        return processbiclusters
    
    def bimaxU(data, R, C, processbiclusters):
        if BiMax.isCluster(data, R, C):
            processbiclusters.append([R]+[C])
            return
        UR, UC, VR, VC = BiMax.getUV(data, R, C)
        if len(UR) > 1:      
            BiMax.bimaxU(data, UR, UC, processbiclusters)
        if len(VR) > 1:
            BiMax.bimaxU(data, VR, VC, processbiclusters)   
        return processbiclusters
        
    def bimaxV(data, R, C, processbiclusters, Z):
        if BiMax.isCluster(data, R, C):
            if BiMax.isDuplicate(Z, C):
                return
            processbiclusters.append([R]+[C])
            return
        UR, UC, VR, VC = BiMax.getUV(data, R, C)
        if len(UR) > 1:      
            BiMax.bimaxV(data, UR, UC, processbiclusters, Z)
        if len(VR) > 1:
            BiMax.bimaxV(data, VR, VC, processbiclusters, Z)   
        return processbiclusters

    def getKleeneRow(data, R, C):
        for r in R:
            for c in C:
                if data[r][c] == 0:
                    return r
    
    def getC_U(data, kleenerow, C):
        C_U = set()
        for c in C:
            if data[kleenerow][c] == 1:
                C_U.add(c)
        return C_U
    
    def getR_UVW(data, C_U, R, C):
        R_U = set()
        R_V = set()
        R_W = set()
        for r in R:
            c_uflag = False
            c_vflag = False
            for c in C:
                if data[r][c] == 1:
                    if not set([c]).isdisjoint(C_U):
                        c_uflag = True
                    else:
                        c_vflag = True
                    if c_uflag and c_vflag:
                        break
            if c_uflag and c_vflag:
                R_W.add(r)
            elif c_uflag:
                R_U.add(r)
            else:
                R_V.add(r)
        return R_U, R_V, R_W
    
    def isCluster(data, R, C):
        for r in R:
            for c in C:
                if data[r][c] == 0:
                    return False
        return True
    
    def getUV(data, R, C):
        kleenerow = BiMax.getKleeneRow(data, R, C)
        C_U = BiMax.getC_U(data, kleenerow, C)
        C_V = set(C) - C_U
        R_U, R_V, R_W = BiMax.getR_UVW(data, C_U, R, C)
        UR = list(R_U | R_W)
        UC = list(C_U)
        VR = list(R_W | R_V)
        VC = list(C_U | C_V)
        return UR, UC, VR, VC
    
    def isDuplicate(Z, C):
        if set(C).isdisjoint(Z):
            return True
        else:
            return False