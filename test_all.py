import sys, os, urllib.request
import cv2
import image_processing
import pillbox_interface


def eval_search_results(results, img_fn):
	pill_gold_standard = {'a1': 'Regular Strength Enteric coated aspirin - Aspirin 325 MG Delayed Release Oral Tablet',
	 'b1': 'Zegerid OTC - Omeprazole 20 MG / Sodium Bicarbonate 1100 MG Oral Capsule [Zegerid Reformulated Aug 2006]'
	 , 'c1': 'Ondansetron - Ondansetron 4 MG Oral Tablet', 'd1': 'Fludrocortisone Acetate - Fludrocortisone 0.1 MG Oral Tablet',
	 'e1': 'Tizanidine hydrochloride - tizanidine 4 MG Oral Capsule' , 
	 'f1': 'Sulfasalazine - Sulfasalazine 500 MG Oral Tablet' ,
	 'g1': 'Mucinex DM - 12 HR Dextromethorphan Hydrobromide 60 MG / Guaifenesin 1200 MG Extended Release Oral Tablet [Mucinex DM]' , 
	 'h1': ' Benzonatate - benzonatate 200 MG Oral Capsule', 'j1': 'Medique Diphen - Diphenhydramine Hydrochloride 25 MG Oral Tablet', 
	 'i1': '', 
	 'k1': 'Celecoxib - celecoxib 100 MG Oral Capsule', 'l1': 'Aleve - Naproxen sodium 220 MG Oral Tablet [Aleve]' ,
	 'm1': 'Fluoxetine - Fluoxetine 40 MG Oral Capsule'}
	img_fn = img_fn[-6:-4]

	if pill_gold_standard[img_fn] in results:
		# correct_matches += 1
		return 1
	return 0
		# idx = results.index(pill_gold_standard[img_fn])
		# print("results contain correct label at result " + str(idx) + ' out of ' + str(len(results)))
	# else: 
	# 	print("results do not contain correct label")

def eval_feature_results(desc, img_fn):
	pill_gold_standard = {'a1': {'color': 'orange', 'shape': 'round', 'size': '9', 'score': '1', 'imprint': '44 227' }, 
	'b1': {'color': 'white', 'shape': 'capsule', 'size': '23', 'score': '1', 'imprint': 'ZEG 20' },
	 'c1':  {'color': 'white', 'shape': 'oval', 'size': '10', 'score': '1', 'imprint': 'G1 4' } , 
	 'd1': {'color': 'yellow', 'shape': 'oval', 'size': '9', 'score': '2', 'imprint': 'b 99 1 10' },
	 'e1': {'color': 'blue white', 'shape': 'capsule', 'size': '16', 'score': '1', 'imprint': '4 MG' }, 
	 'f1': {'color': 'yellow', 'shape': 'round', 'size': '14', 'score': '2', 'imprint': 'WATSON 796' } ,
	 'g1': {'color': 'white', 'shape': 'oval', 'size': '22', 'score': '1', 'imprint': 'MUCINEX 1200' } , 
	 'h1': {'color': 'yellow', 'shape': 'oval', 'size': '19', 'score': '1', 'imprint': '106' }, 
	 'j1': {'color': 'pink', 'shape': 'oval', 'size': '11', 'score': '1', 'imprint': 'T 061' }, 
	 'i1': '', 
	'k1': {'color': 'blue white', 'shape': 'capsule', 'size': '18', 'score': '1', 'imprint': 'TEVA 7165' }, 
	'l1': {'color': 'blue', 'shape': 'oval', 'size': '12', 'score': '1', 'imprint': 'ALEVE' } , 
	'm1': {'color': 'blue', 'shape': 'capsule', 'size': '19', 'score': '1', 'imprint': '40 A107' } }

	img_fn = img_fn[-6:-4]

	total_fields = 4

	mismatched = 0

	for key in desc:
		if key == 'size':
			if abs(int(desc[key]) - int(pill_gold_standard[img_fn][key])) > 2:
				mismatched += 1
		elif key == 'imprint':
			if pill_gold_standard[img_fn][key].find(desc[key]) == -1:
				mismatched += 1
		elif key == 'color':
			if pill_gold_standard[img_fn][key].find(desc[key]) == -1:
				mismatched += 1
		elif pill_gold_standard[img_fn][key] != desc[key]:
			mismatched += 1
	temp = total_fields - mismatched
	return temp
	# correct_features += temp
	# print(str(mismatched) + ' out of ' + str(total_fields) + ' features misidentified')


correct_matches = 0
correct_features = 0
total = 0

dir_contents = os.listdir()

bg_fn = 'bg-flash.jpg'

bg = pillbox_interface.get_bg(bg_fn)

for f in dir_contents:
	if f[-5:] == '1.jpg':
		total += 1
		img = pillbox_interface.get_image(f)
		desc = image_processing.get_pill_description(img, bg)
		query_url = pillbox_interface.create_url(desc)
		response = urllib.request.urlopen(query_url)
		results = pillbox_interface.parse_response(response)

		correct_features += eval_feature_results(desc, f)
		correct_matches += eval_search_results(results, f)

print('Correctly identified ' + str(correct_features) + ' out of ' + str(total * 4) + ' features')
print('Correctly identified ' + str(correct_matches) + ' out of ' + str(total) + ' pills')