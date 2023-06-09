import stanza


# http://nlpviz.bpodgursky.com/
# https://cs.nyu.edu/~grishman/jet/guide/PennPOS.html
class UserDialogueAct:
    def __init__(self,verbsFinal,complements,modifiers,sentiment):
            self.verbs=verbsFinal
            self.complements=complements
            self.modifiers=modifiers
            self.sentiment=sentiment



class LanguageUnderstanding:
    def __init__(self):
        self.nlp = stanza.Pipeline('en',
                              processors='tokenize,sentiment,mwt,pos,lemma,depparse,ner,constituency')  # initialize English neural pipeline
    def preProcess(self,phrase):
        phrase = phrase.capitalize()
        while "can't" in phrase:
            phrase = phrase.replace("can't","can not")
        return phrase


    def extract_lemma(self,phrase, dictionary):
        """ Extracts the test verb  of the phrase given a set of possible lemmas """
        verbs = []
        visited_node = []
        complement = None
        adverb = []
        for elem in phrase.sentences[0]._words:
            if (elem.lemma in dictionary):
                verbs.append(elem)
        '''
        for verb in verbs:
            for elem in phrase.sentences[0]._words:
                if verb.id not in visited_node :
                    visited_node.append(verb.id)
                    if (elem.head == verb.head and elem.xpos == "RB"):
                        adverb.append(elem)
                    if (elem.id == verb.head):
                        complement = elem
        '''
        return verbs


    def elaborateModifier(self,modifiers):
        """ Groups together some modifiers of the verb to make it easier later to work """
        result = []
        for modifier in modifiers:
            if modifier == "not" or modifier == "n't":
                result.append("!")
            else:
                result.append(modifier)
        return result


    def elaborateComplement(self,root):
        """ Extracts child elements from the complement sub-tree """
        complements = []
        for child in root.children:
            if (len(child.children) == 0):
                if (child.label == "or"):
                    complements.append("|")
                elif (child.label == "not"):
                    complements.append("!")
                elif (child.label == "and" or child.label == ","):
                    complements.append("&")
                else:
                    complements.append(child.label)
            else:
                complements.extend(self.elaborateComplement(child))
        return complements


    def mergeComplements(self,complements, modifiers):
        """ Applies logic rules based on the modifiers to the complements """
        if (len(complements) == 0):
            return []
        # Unisco i complementi
        index = 0
        while (index < len(complements) - 1):
            # Se la cella attuale è una parola e se la cella successiva è una parola
            if (complements[index] != "!" and complements[index] != "&" and complements[index] != "|") and (
                    complements[index + 1] != "!" and complements[index + 1] != "&" and complements[index + 1] != "|"):
                # Merge delle parole
                complements[index] = complements[index] + " " + complements[index + 1]
                complements.remove(complements[index + 1])
                # Resetto la ricerca
                index = 0
            else:
                index = index + 1

        # Applico le negazioni locali
        for i in range(len(complements)):
            if (complements[i] == "!"):
                if (complements[i + 1] == "!"):
                    complements[i + 1] = ""
                else:
                    complements[i + 1] = "!" + complements[i + 1]
                complements[i] = ""
        while (complements.count("") > 0):
            complements.remove("")
        # Applico le negazioni globali
        if ("!" in modifiers):
            for i, complement in enumerate(complements):
                if (complement.startswith("!")):
                    complements[i] = complement[1:]
                else:
                    if (complement == "&"):
                        complements[i] = "|"
                    elif (complement == "|"):
                        complements[i] = "&"
                    else:
                        complements[i] = "!" + complement
        return complements


    def get_leaf_nodes(self,sentence):
        """ Extract all the leaf nodes from the tree and adds the parent reference in each node """
        leafs = []
        verbs = []

        def _get_leaf_nodes(node, parent):
            if node is not None:
                node.parent = parent
                if node.label=="VP" or node.label=="VBZ" or node.label=="VB":
                    verbs.append(0)
                if len(node.children) == 0:
                    leafs.append(node)
                for n in node.children:
                    _get_leaf_nodes(n, node)

        _get_leaf_nodes(sentence.children[0], None)
        return (leafs,len(verbs))


    def findComplement(self,node):
        """ Extracts the subtree relative to the complement of the verb"""
        foundNode = None
        if (node.label == "NP" or node.label == "ADJP" or node.label == "NNP"):
            foundNode = node
        else:
            index = 0
            while (index < len(node.children) and foundNode == None):
                foundNode = self.findComplement(node.children[index])
                index = index + 1

        return foundNode


    def findComplement_no_verb(self,node):
        """ Extracts the subtree relative to the complement of the verb"""
        foundNode = None
        if (node.label == "NP" or node.label == "ADJP" or node.label == "NNP" or node.label == "LS" or node.label == "UH"):
            foundNode = node
        else:
            index = 0
            while (index < len(node.children) and foundNode == None):
                foundNode = self.findComplement_no_verb(node.children[index])
                index = index + 1

        return foundNode


    def findModifiers(self,node):
        """ Extracts the modifiers of the verb """
        foundNodes = []
        if (hasattr(node, "parent") and node.parent != None):
            if (node.parent.label == "VP"):
                foundNodes = self.findModifiers(node.parent)
        if (node.label == "RB" or node.label == "RBR" or node.label == "RBS" or node.label == "ADVP"):
            child = node.children[0]
            foundNodes.append(child.label)
        else:
            for child in node.children:
                if (child.label == "RB" or node.label == "RBR" or node.label == "RBS" or node.label == "ADVP"):
                    foundNodes.append(child.children[0].label)
        return foundNodes


    def findModifier_no_verb(self,node):
        foundNodes = []
        if (node.label == "RB" or node.label == "MD" or node.label == "ADVP"):
            for child in node.children:
                if (
                        child.label != "RB" and child.label != "MD" and child.label != "ADVP" and child.label != "NNP" and child.label != "NP"):
                    foundNodes.append(child.label)
        for child in node.children:
            foundNodes.extend(self.findModifier_no_verb(child))
        return foundNodes


    def understand_answer_no_verb(self,sentence):
        complements = []
        modifiers = []
        complementBlock = None
        modifierBlock = None
        local_modifiers = None
        local_complements = None
        #print(sentence)
        while (sentence.label == "ROOT"):
            sentence = sentence.children[0]
        complementBlock = self.findComplement_no_verb(sentence)
        modifierBlock = self.findModifier_no_verb(sentence)
        local_modifiers = self.elaborateModifier(modifierBlock)
        if (complementBlock != None):
            local_complements = self.elaborateComplement(complementBlock)
        else:
            local_complements = []
        local_complements = self.mergeComplements(local_complements, local_modifiers)
        complements.append(local_complements)
        modifiers.append(local_modifiers)
        return (complements, modifiers)


    def understand_answer(self,phrase, suggested_verbs):
        # doc = nlp("I think that it be not 3 or 5, it be 1 or 2, You must make 4 and 6")  # run annotation over a sentence
        doc = self.nlp(self.preProcess(phrase))  # run annotation over a sentence
        sent = doc._sentences[0]._constituency
        (leaf_nodes,verb_count) = self.get_leaf_nodes(sent) #While we explore the tree we estimate how many verbs are there
        print("cont verb",verb_count)
        print("sentiment",doc.sentences[0].sentiment)
        complements = []
        modifiers = []
        verbsFinal = []
        verbs = self.extract_lemma(doc, suggested_verbs)
        if (verb_count == 0):       #If there are no verbs we use a different analysis
            (complements, modifiers) = self.understand_answer_no_verb(sent)
            verbsFinal = [[]]
        else:
            local_modifiers = None
            local_complements = None
            for verb in verbs:
                complementBlock = None
                modifierBlock = None
                current_verb = verb._text
                for node in leaf_nodes:
                    try:
                        if (node.label == current_verb):
                            verb = node
                            leaf_nodes.pop(leaf_nodes.index(node))
                            exploreNode = verb
                            while (exploreNode.label != "VP" and node.label!="VBZ" and node.label!="VB"):
                                exploreNode = exploreNode.parent
                            complementBlock = self.findComplement(exploreNode)
                            modifierBlock = self.findModifiers(exploreNode)
                            local_modifiers = self.elaborateModifier(modifierBlock)
                            if (complementBlock != None):
                                local_complements = self.elaborateComplement(complementBlock)
                            else:
                                local_complements = []
                            local_complements = self.mergeComplements(local_complements, local_modifiers)
                            verbsFinal.append(verb)
                            break
                    except Exception as e:
                        local_modifiers = [None]
                        local_complements = [None]
                        print("Error")
                        print(e)

            if(local_complements!=None and local_modifiers!=None and len(local_complements)==0 and len(local_modifiers)==1 and "!" in local_modifiers):
                local_complements.append("not")
                local_modifiers.pop()
            complements.append(local_complements)
            modifiers.append(local_modifiers)

        print("verbsFinal",verbsFinal)
        print("complements final",complements)
        print("modifiers final",modifiers)
        return UserDialogueAct(verbsFinal,complements,modifiers,doc.sentences[0].sentiment)

if __name__ == "__main__":
    #understand_answer("Yes he isn't", ["be","can","can't"])
    understanding=LanguageUnderstanding()
    questions = ["How old are you?","In which country does Rome reside?","Can a priest get married?"]
    #questions = ["Can a priest get married?"]
    replay="yes"
    while replay == "yes":
        for quest in questions:
            print(quest)
            ans=input()
            understanding.understand_answer(ans,["be","reside","can","can't"])
        print("Do you wanna continue?")
        replay = input()
