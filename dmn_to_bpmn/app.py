from library.DMNImport import DMNImport
from library.DMNVisualisation import DMNVisualisation
from library.definitions.Elements import *
from library.definitions.Requirements import *

import graphviz as gv
import os
from collections import defaultdict 


dmn_path = ''
model = DMNImport.load_model_from_xml(dmn_path)
graph = gv.Digraph()


#predifine names of datbases
predifined = list()
done = False
while done == False:
    input_string = input("Enter name of database, if done enter done\n")
    if input_string == "done": done = True
    else: predifined.append(input_string)

#creation of authority relations
know = defaultdict(list) 
for requirement in model.requirement_list:
    if isinstance(requirement, AuthorityRequirement):
        know[requirement.from_elem.name].append(requirement.to_elem.name)


#transformation of dmn nodes to bpmn
names = list()
know2=defaultdict(list) 
for element in model.element_list:
    name = element.name
    names.append(name)
    if isinstance(element, DecisionElement):
        if element.information_requirement_list != None:
            for i in element.information_requirement_list:

                a = graph.node(name, label = DMNVisualisation.break_name(name), shape = 'none', image = DMNVisualisation.path_to_img + 'task.png')
            
                if isinstance(i, KnowledgeSourceElement):
                    continue

                if "request" in i.name.lower():
                    know2[element.name].append(i.name)
                    b = graph.node(i.name, label = DMNVisualisation.break_name(i.name), shape = 'none', image = DMNVisualisation.path_to_img + 'request.png')
                    graph.edge(i.name, name)

                elif "report" in i.name.lower()  or "document" in i.name.lower() or "info" in i.name.lower():
                    know2[element.name].append(i.name)
                    b = graph.node(i.name, label = DMNVisualisation.break_name(i.name), shape = 'none', image = DMNVisualisation.path_to_img + 'report.png')
                    graph.edge(i.name, name, style = 'dashed', arrowhead = 'dot')

                elif "database" in i.name.lower() or i.name in predifined:
                    know2[element.name].append(i.name)
                    b = graph.node(i.name, label = DMNVisualisation.break_name(i.name), shape = 'none', image = DMNVisualisation.path_to_img + 'database.png')
                    graph.edge(i.name, name, style = 'dashed')
                
                else:
                    know2[element.name].append(i.name)
                    b = graph.node(i.name, label = DMNVisualisation.break_name(i.name), shape = 'none', image = DMNVisualisation.path_to_img + 'task.png')
                    graph.edge(i.name, name)


#adding pools/authorithies
tuples = list()
for key in know.keys():
    edgee = defaultdict(list)
    for item in know[key]:
        done = False
        while done == False:
            
            input_string = input("Enter name of processes that need authority of "+ key+ " in "+item+"\n"+
            ' '.join([str(elem) for elem in know2[item]])+ "\n"+
            "Enter done if done\n")

            if input_string == "done": done = True
            else: edgee[item].append(input_string) 

    edgee= dict(edgee)
    for key2 in edgee.keys():
        for i in edgee[key2]:
            tuples.append((i,key2))

    with graph.subgraph(name="cluster_"+key) as c:
        c.attr('edge', style='invis')
        c.edges(tuples)
        c.attr(label=key)    


#start and end nodes
start = input("Enter name of start node out of those nodes: "+ ', '.join(names)+"\n")
end = input("Enter name of end node out of those nodes: "+ ', '.join(names)+"\n")

graph.node("end", shape = "circle", style='filled', fillcolor = "black")
graph.edge(end, "end")

graph.node("start", shape = "doublecircle")
graph.edge("start", start)


graph.render("result", view = True)
