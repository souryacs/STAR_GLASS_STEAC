#!/usr/bin/env python

"""
program for species tree estimation
computes four criteria - 
1) Sum of deep coalescence
2) Rank statistics 
3) Min coalescence time
4) Avg coalescence time
"""

import dendropy
from optparse import OptionParser
import math
import time
import os
import numpy
#import matplotlib.pyplot as plt
#import pylab

""" this dictionary defines the taxa pair relations
each entry is indexed by two nodes """
TaxaPair_Reln_Dict = dict()

# this text file stores all the printing output
Output_Text_File = 'complete_output_description.txt'

# this is the debug level
# set for printing the necessary information
DEBUG_LEVEL = 0

## this is for plotting various statistical parameters
## computed using the input gene trees
#PLOTTING_ENABLED = 0

# methods implemented in the current package
STAR = 1
GLASS = 2
STEAC = 3

##-----------------------------------------------------
""" 
this class defines the connectivity relationship between a pair of taxa
initially the information are obtained from the input source trees
"""
class Reln_TaxaPair(object):  
  def __init__(self):
    # this is the count of trees for which the couplet is supported
    self.tree_support_count = 0        
    # this list contains the rank information corresponding to the MRCA nodes
    # for this taxa pair in different source gene trees
    self.rank_statistics_list = []
    # this list contains the coalescence information
    # branch length distance between individual leaves to their MRCA nodes
    # for all the source trees
    self.coalescence_time_list = []
    
  ## histogram plotting
  #def PlotHist(self, inp_key, inp_no, outdir, inp_str):
    #title_str = 'Histogram of ' + inp_str + ' for the couplet ' + str(inp_key[0]) + ' and ' + str(inp_key[1])
    #if (inp_no == 11):
      #arr = self.rank_statistics_list
    #elif (inp_no == 21) or (inp_no == 31):
      #arr = self.coalescence_time_list
    #elif (inp_no == 41):
      #arr = self.extra_lineage_sum_list
    #elif (inp_no == 42):
      #arr = self.lineage_sum_list
    #elif (inp_no == 43):
      #arr = self.level_info_list
    #elif (inp_no == 44):
      #arr = self.score_product_xl_level_list
    #elif (inp_no == 51):
      #arr = self.accumulated_rank_list
      
    ## the histogram of the data
    #n, bins, patches = plt.hist(arr, bins=100, normed=0, facecolor='g', alpha=0.75, hold=False)
    #plt.xlabel(inp_str)
    #plt.ylabel('Count')
    #plt.title(title_str)
    ##plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    ##plt.axis([40, 160, 0, 0.03])
    #plt.grid(True)
    ##plt.show()  
    #output_image_filename = outdir + inp_str + '_' + str(inp_key[0]) + '_and_' + str(inp_key[1]) + '.jpg'
    #pylab.savefig(output_image_filename)	# saves the figure in custom specified image
        
  # this function adds the count of tree according to the support of 
  # corresponding couplet in the input tree
  def _IncrSupportTreeCount(self):
    self.tree_support_count = self.tree_support_count + 1
          
  # this function returns the number of trees supporting the couplet
  def _GetSupportTreeCount(self):
    return self.tree_support_count        
    
  #def _AddScoreProductXLLevel(self, val):
    #self.score_product_xl_level_list.append(val)
    
  #def _AddLevel(self, val):
    #self.level_info_list.append(val)
    
  #def _AddTotalLineage(self, val):
    #self.lineage_sum_list.append(val)
    
  #def _AddAccumulatedRank(self, val):
    #self.accumulated_rank_list.append(val)
    
  # this function adds one rank information of this taxa pair
  # corresponding to one input gene tree
  def _AddRankInfo(self, rank_val):
    self.rank_statistics_list.append(rank_val)
        
  # computes the average ranking information for this taxa pair
  def _GetAvgRank(self):
    return (sum(self.rank_statistics_list) * 1.0) / self.tree_support_count
  
  # computes the minimum of the rank information
  def _GetMinRank(self):
    return min(self.rank_statistics_list)

  # computes the minimum of the rank information
  def _GetMaxRank(self):
    return max(self.rank_statistics_list)
  
  # this function adds the coalescence time information
  # corresponding to one input gene tree
  # 1st arg - distance from taxa 1 to MRCA
  # 2nd arg - distance from taxa 2 to MRCA
  # 3rd arg - sum of distances from taxa 1 to taxa 2
  def _AddCoalescenceInfo(self, coalescence_sum):
    self.coalescence_time_list.append(coalescence_sum)  
  
  # computes the average coalescence time information for this taxa pair
  def _GetAvgCoalescenceTime(self):
    return sum(self.coalescence_time_list) / len(self.coalescence_time_list)
      
  # computes the minimum coalescence time information for this taxa pair  
  def _GetMinCoalescenceTime(self):
    return min(self.coalescence_time_list)

  # computes the minimum coalescence time information for this taxa pair  
  def _GetMaxCoalescenceTime(self):
    return max(self.coalescence_time_list)
      
  ## this function adds one extra lineage value of this taxa pair
  ## corresponding to one input gene tree
  #def _AddExtraLineageCountInfo(self, xl_val):
    #self.extra_lineage_sum_list.append(xl_val)
      
  ## get the sum of extra lineages of this couplet
  ## with respect to all the input gene trees
  #def _GetSumExtraLineage(self):
    #return sum(self.extra_lineage_sum_list)

  ## get the sum of extra lineages of this couplet
  ## with respect to all the input gene trees
  #def _GetAvgExtraLineage(self):
    #return (sum(self.extra_lineage_sum_list) * 1.0) / self.tree_support_count
      
  # this function prints information for the current couplet
  def _PrintTaxaPairRelnInfo(self, key, METHOD_USED, out_text_file):
    fp = open(out_text_file, 'a')    
    fp.write('\n taxa pair key: ' + str(key))
    if (METHOD_USED == STAR):
      fp.write('\n *** rank info --- min: ' + str(self._GetMinRank()) \
	+ ' max: ' + str(self._GetMaxRank()) + ' avg: ' + str(self._GetAvgRank()))
    elif (METHOD_USED == GLASS) or (METHOD_USED == STEAC):
      fp.write('\n *** coalescence time info --- min: ' + str(self._GetMinCoalescenceTime()) \
	+ ' max: ' + str(self._GetMaxCoalescenceTime()) + ' avg: ' + str(self._GetAvgCoalescenceTime()))
    fp.close()
    
  ## this function plots various statistics distribution
  #def _PlotStatistics(self, key, METHOD_USED, out_dir):
    #if (METHOD_USED == STAR):
      #self.PlotHist(key, 11, out_dir, 'coalescence rank')
    #if (METHOD_USED == GLASS): 
      #self.PlotHist(key, 21, out_dir, 'coalescence time')
    #if (METHOD_USED == STEAC):
      #self.PlotHist(key, 31, out_dir, 'coalescence time')
    #if (METHOD_USED == 4):
      #self.PlotHist(key, 41, out_dir, 'extra lineage sum')
      #self.PlotHist(key, 42, out_dir, 'total lineage sum')
      #self.PlotHist(key, 43, out_dir, 'level (branch) count')
      #self.PlotHist(key, 44, out_dir, 'product XL and level')
    #if (METHOD_USED == 5):
      #self.PlotHist(key, 51, out_dir, 'accumulated coalescence rank')
      
    #return
      