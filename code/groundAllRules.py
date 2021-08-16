import time
import os

class GroundAllRules():
    def __init__(self):
        self.triples = []
        self.entity2id = dict()
        self.relation2id = dict()
        self.training2label = dict()
        self.relation2Tuple = dict()
        self.RelSub2Obj = dict()
        self.MapVariable = dict()

    def readData(self, RelationIDMap, EntityIDMap, TrainingTriples):
        with open(EntityIDMap) as fin:
            for line in fin:
                eid, entity = line.strip().split('\t')
                self.entity2id[entity] = int(eid)

        with open(RelationIDMap) as fin:
            for line in fin:
                rid, relation = line.strip().split('\t')
                self.relation2id[relation] = int(rid)

        print("Start to load soft rules......")
        with open(TrainingTriples) as fin:
            for line in fin:
                h, r, t = line.strip().split('\t')
                iRelationID = self.relation2id[r]
                strValue = h + "#" + t
                self.training2label[line] = True
                if iRelationID not in self.relation2Tuple:
                    tmp = list()
                    tmp.append(strValue)
                    self.relation2Tuple[iRelationID] = tmp
                else:
                    self.relation2Tuple[iRelationID].append(strValue)

        with open(TrainingTriples) as fin:
            for line in fin:
                h, r, t = line.strip().split('\t')
                iSubjectID = self.entity2id[h]
                iRelationID = self.relation2id[r]
                iObjectID = self.entity2id[t]
                if iRelationID not in self.RelSub2Obj:
                    tmpMap = dict()
                    if iSubjectID not in tmpMap:
                        tmpMap_in = dict()
                        tmpMap_in[iObjectID] = True
                        tmpMap[iSubjectID] = tmpMap_in
                    else:
                        tmpMap[iSubjectID][iObjectID] = True
                    self.RelSub2Obj[iRelationID] = tmpMap
                else:
                    tmpMap = self.RelSub2Obj[iRelationID]
                    if iSubjectID not in tmpMap:
                        tmpMap_in = dict()
                        tmpMap_in[iObjectID] = True
                        tmpMap[iSubjectID] = tmpMap_in
                    else:
                        tmpMap[iSubjectID][iObjectID] = True
        print("readData Success!")

    def groundRule(self, RuleType, Output):
        print("Start to propositionalize soft rules......")
        tmpLst = dict()
        writer = open(Output, "w")
        with open(RuleType) as reader:
            for line in reader:
                if line[0] != '?':
                    continue
                bodys = line.split("=>")[0].strip().split("  ")
                heads = line.split("=>")[1].strip().split("  ")

                if len(bodys) == 3:
                    bEntity1 = bodys[0]
                    iFstRelation = self.relation2id[bodys[1]]
                    bEntity2 = bodys[2]

                    hEntity1 = heads[0]
                    iSndRelation = self.relation2id[heads[1]]
                    hEntity2 = heads[2].split("\t")[0]
                    confidence = heads[2].split("\t")[1]
                    confi = float(confidence)

                    iSize = len(self.relation2Tuple[iFstRelation])
                    for iIndex in range(iSize):
                        strValue = self.relation2Tuple[iFstRelation][iIndex]
                        iSubjectID = self.entity2id[strValue.split("#")[0]]
                        iObjectID = self.entity2id[strValue.split("#")[1]]
                        self.MapVariable[bEntity1] = iSubjectID
                        self.MapVariable[bEntity2] = iObjectID
                        strKey = "(" + str(iSubjectID) + "\t" + str(iFstRelation) + "\t" + str(iObjectID) + ")\t" + "(" + str(self.MapVariable[hEntity1]) + "\t" + str(iSndRelation) + "\t" + str(self.MapVariable[hEntity2]) + ")"
                        strCons = str(self.MapVariable[hEntity1]) + "\t" + str(iSndRelation) + "\t" + str(self.MapVariable[hEntity2])
                        if (strKey not in tmpLst) and (strCons not in self.training2label):
                            writer.write("2\t" + str(strKey) + "\t" + str(confi) + "\n")
                            tmpLst[strKey] = True
                        self.MapVariable.clear()

                elif len(bodys) == 6:
                    bEntity1 = bodys[0].strip()
                    iFstRelation = self.relation2id[bodys[1].strip()]
                    bEntity2 = bodys[2].strip()

                    bEntity3 = bodys[3].strip()
                    iSndRelation = self.relation2id[bodys[4].strip()]
                    bEntity4 = bodys[5].strip()

                    hEntity1 = heads[0].strip()
                    iTrdRelation = self.relation2id[heads[1].strip()]
                    hEntity2 = heads[2].split("\t")[0].strip()
                    confidence = heads[2].split("\t")[1].strip()
                    confi = float(confidence)

                    mapFstRel = self.RelSub2Obj[iFstRelation]
                    mapSndRel = self.RelSub2Obj[iSndRelation]
                    lstEntity1 = iter(mapFstRel.keys())
                    for iEntity1ID in lstEntity1:
                        self.MapVariable[bEntity1] = iEntity1ID
                        lstEntity2 = list(mapFstRel[iEntity1ID].keys())
                        iFstSize = len(lstEntity2)
                        for iFstIndex in range(iFstSize):
                            iEntity2ID = lstEntity2[iFstIndex]
                            self.MapVariable[bEntity1] = iEntity1ID
                            self.MapVariable[bEntity2] = iEntity2ID
                            lstEntity3 = list()
                            if (bEntity3 in self.MapVariable) and (self.MapVariable[bEntity3] in mapSndRel):
                                lstEntity3.append(self.MapVariable[bEntity3])
                            elif bEntity3 not in self.MapVariable:
                                lstEntity3 = list(mapSndRel.keys())
                            iSndSize = len(lstEntity3)
                            for iSndIndex in range(iSndSize):
                                iEntity3ID = lstEntity3[iSndIndex]
                                self.MapVariable[bEntity1] = iEntity1ID
                                self.MapVariable[bEntity2] = iEntity2ID
                                self.MapVariable[bEntity3] = iEntity3ID
                                lstEntity4 = list()
                                if (bEntity4 in self.MapVariable) and (self.MapVariable[bEntity4] in mapSndRel[iEntity3ID]):
                                    lstEntity4.append(self.MapVariable[bEntity4])
                                elif bEntity4 not in self.MapVariable:
                                    lstEntity4 = list(mapSndRel[iEntity3ID].keys())
                                iTrdSize = len(lstEntity4)
                                for iTrdIndex in range(iTrdSize):
                                    iEntity4ID = lstEntity4[iTrdIndex]
                                    self.MapVariable[bEntity4] = iEntity4ID
                                    infer = str(self.MapVariable[hEntity1]) + "\t" + str(iTrdRelation) + "\t" + str(self.MapVariable[hEntity2])
                                    strKey = "(" + str(iEntity1ID) + "\t" + str(iFstRelation) + "\t" + str(iEntity2ID) + ")\t" + "(" + str(iEntity3ID) + "\t" + str(iSndRelation) + "\t" + str(iEntity4ID) + ")\t" + "(" + str(self.MapVariable[hEntity1]) + "\t" + str(iTrdRelation) + "\t" + str(self.MapVariable[hEntity2]) + ")"
                                    if (strKey not in tmpLst) and (infer not in self.training2label):
                                        writer.write("3\t" + str(strKey) + "\t" + str(confi) + "\n")
                                        tmpLst[strKey] = True
                                self.MapVariable.clear()
                            self.MapVariable.clear()
                        self.MapVariable.clear()
        print("groundRule Success!")


if __name__ == '__main__':
    RelationIDMap = "../dataset/fb15k/relations.dict"
    EntityIDMap = "../dataset/fb15k/entities.dict"
    RuleType = "../dataset/fb15k/fb15k_rule"
    TrainingTriples = "../dataset/fb15k/train.txt"
    Output = "../dataset/fb15k/groundings.txt"

    startTime = time.time()
    generator = GroundAllRules()
    generator.readData(RelationIDMap, EntityIDMap, TrainingTriples)
    generator.groundRule(RuleType, Output)
    endTime = time.time()
    print("All running time:", endTime - startTime, "s")