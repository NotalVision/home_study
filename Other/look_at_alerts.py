import pickle

with open(r'\\nv-nas01\Home_OCT_repository\Clinical_studies\Notal-Home_OCT_study-box3.0\Study_at_home\Data\NH02001\Analysis/alerts/alerts.pkl', 'rb') as f:
    a = pickle.load(f)
    print (a)