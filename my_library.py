def test_load():
  return 'loaded'
  
def cond_prob(table, evidence, evidence_value, target, target_value):
  t_subset = up_table_subset(table, target, 'equals', target_value)
  e_list = up_get_column(t_subset, evidence)
  p_b_a = sum([1 if v==evidence_value else 0 for v in e_list])/len(e_list)
  return p_b_a + .01  #Laplace smoothing factor
  #your function body below - copy and paste then align with parameter names

  t_subset = up_table_subset(full_table, the_target_column, 'equals', the_target_column_value)
  e_list = up_get_column(t_subset, the_evidence_column)
  p_b_a = sum([1 if v==the_evidence_column_value else 0 for v in e_list])/len(e_list)
  return p_b_a

def cond_probs_product(full_table, evidence_row, target_column, target_column_value):
  assert target_column in full_table
  assert target_column_value in up_get_column(full_table, target_column)
  assert isinstance(evidence_row, list)
  assert len(evidence_row) == len(up_list_column_names(full_table)) - 1   # - 1 because subtracting off the target column from full_table

  #your function body below
  evidence_columns = up_list_column_names(full_table)[:-1]
  evidence_complete = up_zip_lists(evidence_columns, evidence_row)
  cond_prob_list = [cond_prob(full_table, x[0], x[1], target_column, target_column_value) for x in evidence_complete]
  return up_product(cond_prob_list)

def naive_bayes(full_table, evidence_row, target_column):
  assert target_column in full_table
  assert isinstance(evidence_row, list)
  assert len(evidence_row) == len(up_list_column_names(full_table)) - 1   # - 1 because subtracting off the target

  #compute P(target=0|...) by using cond_probs_product, finally multiply by P(target=0) using prior_prob
  p0= cond_probs_product(full_table, evidence_row, target_column, 0) * prior_prob(full_table, target_column, 0)

  #do same for P(target=1|...)
  p1 = cond_probs_product(full_table, evidence_row, target_column, 1) * prior_prob(full_table, target_column, 1)

  #Use compute_probs to get 2 probabilities
  neg, pos = compute_probs(p0, p1)
  return [neg,pos]
  #return your 2 results in a list

def prior_prob(full_table, the_column, the_column_value):
  assert the_column in full_table
  assert the_column_value in up_get_column(full_table, the_column)

  #your function body below
  t_list = up_get_column(full_table, the_column)
  p_a = sum([1 if v==the_column_value else 0 for v in t_list])/len(t_list)
  return p_a

def compute_probs(neg,pos):
  p0 = neg/(neg+pos)
  p1 = pos/(neg+pos)
  return [p0,p1]

def metrics(zipped_list):
  assert isinstance(zipped_list, list)
  assert all([isinstance(v, list) for v in zipped_list])
  assert all([len(v)==2 for v in zipped_list])
  assert all([isinstance(a,(int,float)) and isinstance(b,(int,float)) for a,b in zipped_list]), f'zipped_list contains a non-int or non-float'
  assert all([float(a) in [0.0,1.0] and float(b) in [0.0,1.0] for a,b in zipped_list]), f'zipped_list contains a non-binary value'

  #first compute the sum of all 4 cases. See code above
  tn = sum([1 if pair==[0,0] else 0 for pair in zipped_list])
  tp = sum([1 if pair==[1,1] else 0 for pair in zipped_list])
  fp = sum([1 if pair==[1,0] else 0 for pair in zipped_list])
  fn = sum([1 if pair==[0,1] else 0 for pair in zipped_list])

 #now compute precision, recall, f1
  precision = tp/(tp+fp) if tp+fp>0 else 0
  recall = tp/(tp+fn) if tp+fn>0 else 0
  f1 = 2*precision*recall/(precision+recall) if precision+recall>0 else 0
  accuracy = (tp+tn)/ len(zipped_list) if len(zipped_list)>0 else 0
  


  #now build dictionary with the 4 measures - round values to 2 places
  mets_dict = {'Precision': round(precision,2), 'Recall': round(recall,2), 'F1': round(f1,2), 'Accuracy': round(accuracy,2)}
  #finally, return the dictionary
  return mets_dict


from sklearn.ensemble import RandomForestClassifier

def run_random_forest(train, test, target, n):
  #target is target column name
  #n is number of trees to use


  assert target in train   #have not dropped it yet
  assert target in test

  #your code below - copy, paste and align from above
  from sklearn.ensemble import RandomForestClassifier
  clf = RandomForestClassifier(n_estimators=n, max_depth=2, random_state=0)   #clf stands for "classifier"
  
  X = up_drop_column(train, target)
  y = up_get_column(train, target )
  assert isinstance(y,list)
  assert len(y)==len(X)

  clf.fit(X, y)

  k_feature_table = up_drop_column(test, target)
  k_actuals = up_get_column(test, target)

  probs = clf.predict_proba(up_drop_column(test,target))  #Note no need here to transform k_feature_table to list - we can just use the table. Nice.

  assert len(probs)==len(k_actuals)
  assert len(probs[0])==2

  pos_probs = [p for n,p in probs]
  all_mets = []
  for t in thresholds:
   predictions = [1 if pos>t else 0 for pos in pos_probs]
   pred_act_list = up_zip_lists(predictions, k_actuals)
   mets = metrics(pred_act_list)
   mets['Threshold'] = t
   all_mets = all_mets + [mets]

  metrics_table = up_metrics_table(all_mets)
  return metrics_table



def try_archs(train_table, test_table, target_column_name, architectures, thresholds):
  arch_acc_dict = {}  #ignore if not attempting extra credit

  #now loop through architectures
  for arch in architectures:
    probs = up_neural_net(train_table, test_table, arch, target_column_name)
    pos_probs = [y for x,y in probs]
    k_actuals = up_get_column(test_table, target_column_name)

    #loop through thresholds
    all_mets = []
    for t in thresholds:
      predictions = [1 if pos>t else 0 for pos in pos_probs]
      pred_act_list = up_zip_lists(predictions, k_actuals)

    #arch_acc_dict[tuple(arch)] = max(...)  #extra credit - uncomment if want to attempt
      mets = metrics(pred_act_list)
      mets['Threshold'] = t
      all_mets = all_mets + [mets]
    arch_acc_dict[tuple(arch)] = max([mets['Accuracy'] for mets in all_mets])
    print(f'Architecture: {arch}')
    display(up_metrics_table(all_mets))

  return arch_acc_dict
