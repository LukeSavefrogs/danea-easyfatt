from zipfile import ZipFile


def kmz_to_kml(filename):
	with ZipFile(filename, 'r') as zip_file:
		with zip_file.open('doc.kml', 'r') as kml_file:
			kml = kml_file.read()
	
	return kml


def main():
	with open("test.kml", "wb") as file:
		file.write(kmz_to_kml("./2023-01-17b.kmz"))

if __name__ == '__main__':
	main()