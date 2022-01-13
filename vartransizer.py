import csv
from rdflib.namespace import DC, RDFS, FOAF, XSD, OWL, RDF
from rdflib import Graph, Namespace
from rdflib.term import URIRef, Literal
import urllib.parse, argparse
import json, re

class Vartransizer():
    def __init__(self, input_tsv, sl, tg, inferenceSys):
        self.input_tsv = input_tsv
        self.source_language = sl
        self.target_language = tg
        self.inference_sys = inferenceSys
        self.base =  "http://linguistic.linkeddata.es/id/apertium/tranSet" \
               + self.source_language.upper() + "-" + self.target_language.upper() + "_" + self.inference_sys + "/"
        self.base_src = "http://linguistic.linkeddata.es/id/apertium/lexicon" \
                   + self.source_language.upper() + "/"
        self.base_tgt = "http://linguistic.linkeddata.es/id/apertium/lexicon" \
                   + self.target_language.upper() + "/"

    def generate_sense_URIs(self):
        sense_URIs = {}
        with open(self.input_tsv, encoding="utf-8") as tsv:
            for line in csv.reader(tsv, delimiter='\t'):
                sense_URIs[line[0]] = {"src_sense_uri": urllib.parse.quote(line[0])
                                                        + "_" + urllib.parse.quote(line[1])
                                                        + "-" + line[3]
                                                        + "-" + self.source_language + "-sense",
                                       "tgt_sense_uri": urllib.parse.quote(line[1])
                                                        + "_" + urllib.parse.quote(line[0])
                                                        + "-" + line[3]
                                                        + "-" + self.target_language + "-sense",
                                       "src_entry_uri": urllib.parse.quote(line[0])
                                                        + "-" + line[3] + "-" + self.source_language,
                                       "tgt_entry_uri": urllib.parse.quote(line[1])
                                                        + "-" + line[3] + "-" + self.target_language,
                                       "confidence": line[4],
                                       "path_pivot":line[5]
                                       }
        with open('sense_dict.json', 'w') as sense_dict:
            jsondict = json.dumps(sense_URIs)
            sense_dict.write(jsondict)
            sense_dict.close()

    def get_graph_bindings (self):
        g = Graph()
        g.namespace_manager.bind('', self.base)
        g.namespace_manager.bind('src', self.base_src)
        g.namespace_manager.bind('tgt', self.base_tgt)
        g.namespace_manager.bind('owl', OWL, override=False)
        g.namespace_manager.bind('dc', DC, override=False)
        g.namespace_manager.bind('rdfs', RDFS, override=False)
        g.namespace_manager.bind('xsd', XSD, override=False)
        g.namespace_manager.bind('rdf', RDF, override=False)
        g.namespace_manager.bind('lexinfo', 'http://www.lexinfo.net/ontology/2.0/lexinfo#')
        g.namespace_manager.bind('ontolex', 'http://www.w3.org/ns/lemon/ontolex#')
        g.namespace_manager.bind('vartrans', 'http://www.w3.org/ns/lemon/vartrans#')
        g.namespace_manager.bind('lime', 'http://www.w3.org/ns/lemon/lime#')
        g.namespace_manager.bind('fuzzyLemon', 'http://sid.cps.unizar.es/def/fuzzyLemon#')
        g.namespace_manager.bind('prov', 'http://www.w3.org/ns/prov#')

        return g

    def generateTransSet(self, graph_bindings, sense_json):
        n = Namespace(self.base)
        ontolex = Namespace("http://www.w3.org/ns/lemon/ontolex#")
        lime = Namespace("http://www.w3.org/ns/lemon/lime#")
        vartrans = Namespace("http://www.w3.org/ns/lemon/vartrans#")
        fuzzyLemon = Namespace("http://sid.cps.unizar.es/def/fuzzyLemon#")
        trans_set_node = URIRef("http://linguistic.linkeddata.es/id/apertium/tranSet"
                                + self.source_language.upper() + "-" \
                                + self.target_language.upper()+"_"+self.inference_sys)

        infer_act_node = URIRef("http://linguistic.linkeddata.es/id/apertium/trans_"+self.inference_sys \
                                +"_infer-activity")
        soft_ag_node = URIRef("http://linguistic.linkeddata.es/id/apertium/trans_"+self.inference_sys \
                              +"_infer-software")

        prov=Namespace("http://www.w3.org/ns/prov#")

        #Add Prov-O Software Agent
        graph_bindings.add((soft_ag_node, RDF.type, prov.SoftwareAgent))
        graph_bindings.add((soft_ag_node, RDFS.label,
                            Literal("Translation Inference system developed at University of Zaragoza"
                       " (UNIZAR) based on Villegas et al. 2016's method for translation "
                       "inference based on cycle density",  lang="en")))

        #Add Prov-O Activity
        graph_bindings.add((infer_act_node, RDF.type, prov.Activity))
        graph_bindings.add((infer_act_node, RDFS.label,
                            Literal("Inference process performed by the " + self.inference_sys + " system.", lang="en")))
        graph_bindings.add((infer_act_node, prov.wasAssociatedWith, soft_ag_node))

        # Add TranslationSet
        graph_bindings.add((trans_set_node, RDF.type, vartrans.TranslationSet))
        graph_bindings.add((trans_set_node, RDFS.label, Literal("Apertium " + self.source_language.upper() +
                                                   "-" + self.target_language.upper()
                                                                + " translation set automatically generated at " \
                                                                + self.inference_sys,
                                                                lang="en")))
        graph_bindings.add((trans_set_node, prov.wasGeneratedBy, infer_act_node))
        graph_bindings.add((trans_set_node, prov.wasAttributedTo, soft_ag_node))
        graph_bindings.add((trans_set_node,
                            RDFS.comment,
                            Literal("This is the RDF version of the set of translations between Apertium lexica for "
                       + self.source_language.upper() + " and " + self.target_language.upper()
                       + " inferred automatically with the " + self.inference_sys + " system. "\
                                    +" The work on translation inference and RDF conversion has been carried out "
                                     "as part of the Prêt-à-LLOD project.".encode("utf-8").decode("utf-8"),
                       lang="en")))
        graph_bindings.add((trans_set_node, lime.language, Literal(source_language)))
        graph_bindings.add((trans_set_node, lime.language, Literal(target_language)))

        # Add Translations
        with open(sense_json, encoding="utf-8") as fi:
            sense_URIs = json.load(fi)
            for entry in sense_URIs.items():
                transURI = entry[1]["src_sense_uri"] + "-" \
                           + entry[1]["tgt_sense_uri"] \
                           + "-trans_"+self.inference_sys
                trans_node = URIRef(self.base + transURI)
                src_sense_node = URIRef(self.base + entry[1]["src_sense_uri"])
                tgt_sense_node = URIRef(self.base + entry[1]["tgt_sense_uri"])
                src_entry_node = URIRef(self.base_src + entry[1]["src_entry_uri"])
                tgt_entry_node = URIRef(self.base_tgt + entry[1]["tgt_entry_uri"])
                graph_bindings.add((trans_node, RDF.type, vartrans.Translation))
                graph_bindings.add((trans_set_node, vartrans.trans, trans_node))
                graph_bindings.add((trans_node, vartrans.source, src_sense_node))
                graph_bindings.add((trans_node, vartrans.target, tgt_sense_node))
                graph_bindings.add((trans_node, vartrans.relates, tgt_sense_node))
                graph_bindings.add((trans_node, vartrans.relates, src_sense_node))
                graph_bindings.add((trans_node, fuzzyLemon.confidenceDegree,
                                    Literal(entry[1]["confidence"], datatype=XSD.float)))
                graph_bindings.add((trans_node, RDFS.comment, Literal("This translation was obtained through the "
                                                         "following path: " + entry[1]["path_pivot"], lang="en")))
                # g.add((n.term(base+transURI), vartrans.relates,src_sense_node))
                graph_bindings.add((src_sense_node, RDF.type, ontolex.LexicalSense))
                graph_bindings.add((tgt_sense_node, RDF.type, ontolex.LexicalSense))
                graph_bindings.add((src_sense_node, ontolex.isSenseOf, src_entry_node))
                graph_bindings.add((tgt_sense_node, ontolex.isSenseOf, tgt_entry_node))
            return graph_bindings


    def generate_rdf(self, graph, format):
        g_string = graph.serialize(format=format, encoding="utf-8").decode("utf-8")
        g_re_string = re.sub("<" + self.base + r"(.+?)(>)", r":\1", g_string)
        g_re_string = re.sub("<" + self.base_src + r"(.+?)(>)", r":\1", g_re_string)
        g_re_string = re.sub("<" + self.base_tgt + r"(.+?)(>)", r":\1", g_re_string)
        ## xsd.decimal not working in the conversion, float does. Replace float by decimal
        ## or leave float as the range of the fuzzyLemon property in the proposed model
        ## TO-CHECK
        g_re_string = re.sub("xsd:float", r"xsd:decimal", g_re_string)
        output_file = "Apertim-"+ self.source_language+"-"+self.target_language+"_TranslationSet"\
                  +self.source_language.upper()+"-"+self.target_language.upper()+".ttl"
        with open(output_file, 'w', encoding="utf-8") as f:
            f.write(g_re_string)


if __name__ == "__main__":
    def get_cl_arguments():
        parser = argparse.ArgumentParser(description='Generate the OntoLex lemon version of a TSV file '
                                                     'with inferred bilingual translations')
        parser.add_argument('-i', "--input", help='The tsv file')
        parser.add_argument('-sl', "--sourceLanguage", help='The source language in the bilingual dictionary')
        parser.add_argument('-tl', "--targetLanguage", help='The target language in the bilingual dictionary')
        parser.add_argument('-infer', "--inferenceSystem", 
                            help='The ending to attach to the generated translation URIs, which represents'
                                 ' the inference system')
        args = parser.parse_args()
        source_language = args.sourceLanguage
        target_language = args.targetLanguage
        inference_sys = args.inferenceSystem
        input_tsv = args.input
        return source_language, target_language, inference_sys, input_tsv

    source_language, target_language, inference_sys, input_tsv = get_cl_arguments()
    vartransizer = Vartransizer(input_tsv, source_language, target_language, inference_sys)
    vartransizer.generate_sense_URIs()
    g = vartransizer.get_graph_bindings()
    complete_graph = vartransizer.generateTransSet(g, "sense_dict.json")
    vartransizer.generate_rdf(complete_graph, "turtle")
