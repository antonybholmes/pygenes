from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import os

from genes import settings

import sys
import libhttp
import libhttpdna
import libgfb
import libgenomic

def _gene_to_json(gene):
    return {'loc':gene.loc, 'strand':gene.strand, 'type':gene.level, 'ids':gene.annotations, 'tags':gene.tags}

def _genes_to_json(genes):
    ret = []
    
    for gene in genes:
        json = _gene_to_json(gene)
        
        if gene.level == libgenomic.GENE:
            json['transcripts'] = _genes_to_json(gene.children(libgenomic.TRANSCRIPT))
        elif gene.level == libgenomic.TRANSCRIPT:
            json['exons'] = _genes_to_json(gene.children(libgenomic.EXON))
        else:
            pass
        
        ret.append(json)
    
    return ret

def about(request):
    return JsonResponse({'name':'genes','version':'1.0','copyright':'Copyright (C) 2018 Antony Holmes'}, safe=False)

def find(request):
    """
    Allow users to search for genes by location
    """
    
    # Defaults should find BCL6
    id_map = libhttp.parse_params(request, {'db':'gencode', 'g':'grch38', 'chr':'chr3', 's':187721377, 'e':187736497, 't':'g'})
    
    db = id_map['db'][0]
    genome = id_map['g'][0]
    
    loc = libhttpdna.get_loc_from_params(id_map)
    
    if loc is None:
        return JsonResponse({}, safe=False)
    
    dir = os.path.join(settings.DATA_DIR, db, genome)
    
    reader = libgfb.GFBReader(db, genome, dir)
    
    genes = reader.find_genes(loc)
    
    gl = _genes_to_json(genes)
    
    return JsonResponse({'loc':loc, 'genes':gl}, safe=False)


def search(request):
    """
    Search for genes by name.
    """
    
    id_map = libhttp.parse_params(request, {'db':'gencode', 'g':'grch38', 's':'BCL6', 't':'g'})
    
    db = id_map['db'][0]
    genome = id_map['g'][0]
    search = id_map['s'][0]
    
    dir = os.path.join(settings.DATA_DIR, db, genome)
    
    reader = libgfb.GFBReader(db, genome, dir)
    
    genes = reader.get_genes(search)
    
    gl = _genes_to_json(genes)
    
    return JsonResponse(gl, safe=False)


def databases(request):
    """
    List available databases.
    """
    
    files = os.listdir(settings.DATA_DIR)
    
    ret = []
    
    for file in files:
        d = os.path.join(settings.DATA_DIR, file)
        if os.path.isdir(d):
            db = file
            
            files2 = os.listdir(d)
            
            for file2 in files2:
                d2 = os.path.join(d, file2)
                
                if os.path.isdir(d2):
                    genome = file2
                    
                    ret.append({'db':db, 'genome':genome})
    
    return JsonResponse(ret, safe=False)
