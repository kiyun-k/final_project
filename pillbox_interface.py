import sys, os
import urllib.request

query_codes = {'blue': '' , 'white': '', 'capsule': '', 'round': '' , 'oval': ''}

def create_url():
	url = 'https://pillbox.nlm.nih.gov/pillimage/search_results.php?'
	search_params = ''
	return url


# Evaluation is a bit rigid: you might want to rank each feature separately (color, size, etc.) before going for the final full match performance.