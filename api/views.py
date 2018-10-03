from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import os

from genes import settings

import sys
sys.path.append('/ifs/scratch/cancer/Lab_RDF/abh2138/scripts/python/lib/libhttp/libhttp')
import libhttp
sys.path.append('/ifs/scratch/cancer/Lab_RDF/abh2138/scripts/python/lib/libgfb/libgfb')
import libgfb

def _genes_to_json(genes):
    ret = []
    
    for gene in genes:
        ret.append({'loc':gene.loc, 'strand':gene.strand, 'type':gene.level, 'ids':gene.annotations, 'tags':gene.tags})
    
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
    
    chr = id_map['chr'][0]
    start = id_map['s'][0]
    end = id_map['e'][0]
    
    if start > end:
      start = start ^ end
      end = start ^ end
      start = start ^ end
    
    loc = '{}:{}-{}'.format(chr, start, end)
    
    dir = os.path.join(settings.DATA_DIR, db, genome)
    
    reader = libgfb.GFBReader(db, genome, dir)
    
    genes = reader.find_genes(loc)
    
    gl = _genes_to_json(genes)
    
    return JsonResponse({'loc':loc, 'genes':gl}, safe=False)


def search(request):
    # Defaults should find BCL6
    id_map = libhttp.parse_params(request, {'db':'gencode', 'g':'grch38', 's':'BCL6', 't':'g'})
    
    db = id_map['db'][0]
    genome = id_map['g'][0]
    search = id_map['s'][0]
    
    dir = os.path.join(settings.DATA_DIR, db, genome)
    
    reader = libgfb.GFBReader(db, genome, dir)
    
    genes = reader.get_genes(search)
    
    gl = _genes_to_json(genes)
    
    return JsonResponse(gl, safe=False)
