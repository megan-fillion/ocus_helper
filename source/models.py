import os
import mysql.connector
from smb.SMBConnection import SMBConnection
from io import BytesIO
import time
import tempfile
import pandas as pd 
import boto3
from tqdm import tqdm
import os, sys
from toto

###Ouiflash database###
class Database:
	def __init__(self, config, connection):
		conf = config[connection]
		self.connect = mysql.connector.connect(host=conf['host'], 
									   		   user=conf['user'], 
									   		   password=conf['password'],
									   		   database=conf['database'],
									   		   ssl_ca= conf['ssl'])  
		self.cursor = self.connect.cursor()

	def execute(self, command):
		self.connect.ping(reconnect=True, attempts=1, delay=0)
		self.cursor.execute(command)
		return self.cursor.fetchall()

	def insert(self, command):		
		self.connect.ping(reconnect=True, attempts=1, delay=0)
		self.cursor.execute(command)
		self.connect.commit()

	def get_labels(self):
		table_des = self.cursor.description
		return [col[0] for col in table_des]

	def close(self):
		self.connect.close()

	###Pandas dataframe functions###
    def select_reseau(self, paths):
        """
        Input : Datascience_path list
        Output : Df of datascience_path and reseau

        Returns the datascience_path with associated reseau in the database.
        Last update 18 May 2020
        """
        query_valid = '''
        	SELECT p.datascience_path, r.nom from `photo_mission` p
        	inner join mission m on m.id = p.id_mission
        	inner join users u on u.id=m.id_agent
        	inner join reseau r on r.id=u.id_reseau
        	WHERE p.datascience_path IN {}
        '''.format(tuple(paths))
        df = pd.DataFrame(self.execute(query_valid))
        df.columns = ['datascience_path', 'reseau']
        return df

    def select_vertical(self, columns, vertical, dataf=True):
        """
        Input : string of vertical in vertical_compta format
        Output : Df with reseau values

        Returns specific vertical from the verticale compta in the reseau table. Needs to be updated regularly with new reseau
        Last update 18 May 2020
        """
        query_vert = '''SELECT {} FROM reseau WHERE verticale_compta = "{}"'''.format(','.join(columns), vertical)
        df = pd.DataFrame(self.execute(query_vert))
        df.columns = columns
        if dataf:
        	return df
        else:
        	return df.values

    def select_paths(self, query):
        """
        Input : SQL format query
        Output : List of datascience paths that verify this query

        Generic method to return paths that verify condition given as Input
        Returns rows where path exists and images have been delivered, limited to the number of rows given in entry
        alternative : version with only light problems
        """
        df = pd.DataFrame(self.execute(query))
        df.columns = ["datascience_path"]
        return df.values

    def select_columns(self, query, dataf=True):
        """
        Input : SQL format Query
        Output : Dataframe of expected columns

        Generic method to select any fields according to any condition
        """
        cursor = self.execute(query)
        df = pd.DataFrame(cursor)
        num_fields = len(cursor.description)
        df.columns = [i[0] for i in cursor.description]
        if dataf:
            return df
        else:
            return df.values


###Nas object connects to Bengio && MediaNef###
class Nas:
	def __init__(self, config, connection):
		conf = config[connection]
		self.ip = conf['ip']
		self.connection = SMBConnection(conf['user'], conf['password'], conf['local_name'], conf['nas_name'])
		self.connection.connect(self.ip)

	def set_root_directory(self, root):
 		self.root = root

	def list_directory(self, path):
		return self.connection.listPath(self.root, path)

	def list_directory_names(self, path):
		dir_raw = self.list_directory(path)
		return [x.filename for x in dir_raw]

	def create_dir(self, path):
		self.connection.createDirectory(self.root, path)
	
	def download_file(self, origin, destination):
		with open(destination, 'wb') as download_file:  # downloading file
			self.connection.retrieveFile(self.root, origin, download_file)

	def download_remote(self, path):
		filename = os.path.basename(path)
		file_obj = BytesIO()
		self.connection.retrieveFile(self.root, path, file_obj)
		return file_obj
 		
	def upload_remote(self, path, file_obj):
		self.connection.storeFile(self.root, path, file_obj)

	def delete_file(self, path):
		self.connection.deleteFiles(self.root, path)
	
	def rename_path(self, origin, destination):
		self.connection.rename(origin, destination)

	def close(self):
 		self.connection.close()


class S3:
    def __init__(self):
        self.client = boto3.client('s3')
        self.resource = boto3.resource('s3')

    def list_objects(self, path, bucket='ouiflash-datascience'):
        list_objects = []
        my_bucket = self.resource.Bucket(bucket)
        for bucket_object in tqdm(my_bucket.objects.filter(Prefix=path)):
            list_objects.append(os.path.basename(bucket_object.key))
        return list_objects

    def download_folder(s3_path, local_path, bucket='ouiflash-datascience'):
		my_bucket = self.resource.Bucket(bucket)
		objects = my_bucket.objects.filter(Prefix=s3_path)

		for obj in tqdm(objects):
			path, filename = os.path.split(obj.key)
			try:
				my_bucket.download_file(obj.key, os.path.join(local_path, filename))
			except Exception as e:
				print(e)
				print(os.path.join(local_path, filename))
				pass
			except KeyboardInterrupt:
				sys.exit()

    def download_files(self, input_data, local_dir, s3_path, bucket='ouiflash-datascience'):
        for index, row in tqdm(input_data.iterrows()):
            mission = int(row["id_mission"])
            md5 = row["md5"]
            file_name = "{}_{}.jpg".format(mission, md5)
            if not os.path.isfile(os.path.join(local_dir, file_name)):
                object_path = os.path.join(s3_path, file_name)
                try:
                    self.client.download_file(bucket, object_path, os.path.join(local_dir, file_name))
                except Exception as e:
                    print(e)
                    print(object_path)
                    pass
                except KeyboardInterrupt:
                    sys.exit()
            else:
                print("The local file already exists")

    def upload_folder(s3_path, local_path, bucket='ouiflash-datascience'):
    	###upload complete folder by feeding in local path###
    	my_bucket = self.resource.Bucket(bucket)
    	for filename in tqdm(os.listdir(local_path)):
    		try:
    			my_bucket.upload_file(os.path.join(local_path, filename), os.path.join(s3_path, filename))
    		except Exception as e:
    			print(e)
    			print(os.path.join(local_path, filename))
    			pass
    		except KeyboardInterrupt:
    			sys.exit()

    def upload_files(s3_path, paths, bucket:'ouiflash-datascience'):
    	###upload certain paths###
    	my_bucket = self.resource.Bucket(bucket)
    	for path in tqdm(paths):
    		try:
    			my_bucket.upload_file(path, os.path.join(s3_path, filename))
	    	except Exception as e:
	    		print(e)
	    		print(path)
	    		pass
	    	except KeyboardInterrupt:
	    		sys.exit()

    def rename(mapped_paths, bucket='ouiflash-datascience'):
    	###Rename files in s3###
    	my_bucket = self.resource.Bucket(bucket)
    	for origin_path in tqdm(mapped_paths.keys()):
    		origin = {'Bucket':bucket, 'key':origin_path}
    		try:
    			my_bucket.copy(origin, mapped_paths[origin_path])
    			self.resource.Object(bucket, origin_path).delete()
    		except Exception as e:
    			print(e)
    			print(origin_path)
    			pass
    		except KeyboardInterrupt:
    			sys.exit()


    def transfer_archived(self, input_data, s3_path, bucket, output_dir):
        ###Download zipfiles from archived missions bucket###
        for index, row in tqdm(input_data.iterrows()):
            mission = int(row["id_mission"])
            file_name = str(mission) + "-livrable.zip"
            if not os.path.isfile(os.path.join(output_dir, file_name)):
                s3_path = os.path.join(str(mission)[:2], str(mission)[2] + str(mission)[3], str(mission), file_name)
                try:
                    self.client.download_file(bucket, s3_path, os.path.join(output_dir, file_name))
                except Exception as e:
                    print(e)
                    print(s3_path)
                    pass
                except KeyboardInterrupt:
                    sys.exit()
            else:
                print("The zip file already exists")
