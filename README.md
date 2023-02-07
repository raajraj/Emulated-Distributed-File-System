The project is based on an emulated distributed file system implemented using Firebase and MySQL, and uses the file system operations implemented and provides these features to the end users.

For the MySQL implementation for partition-based map and reduce on data stored in our EFDS, we performed our following search and analytic functions on our dataset partitions and combined the results.

B.1 MySQL Implementation
For our MySQL implementation, we are using two tables created with the following structure:

fid name parent parentid content file

 ● mkdir()
Creating a new directory is very simple as we just insert a new row into the directory table after gathering all the column information. After parsing through user input and tracking parent information and determining content information, we just insert it.
● ls()
We are able to grab the children files from a directory by simply tracking the parentid grabbed from the file id where the user put in the directory name.
● rm()
For rm() we use a simple delete statement to delete the row from the dir table
● put()
1. Take filename and create a tableName for new table
2. Create a new row in dir table with filename and tableName
3. Create a new table for file contents (.csv, .txt) and assign partition number
4. Insert values into table
5. For each partition, create a new table and insert a new partition location in the
partition table

 ● cat()
For cat(), we use a simple select statement to output the table
● getPartitionLocations()
To get the location of the partitions in the EDFS, we simple map to their IDs in their table
● readPartitions()
To read a partition, we map to the partition table created in put, and map to the part specified by the user
B.2 Firebase Implementation
For our Firebase implementation, we are using 3 cards:
1. Dir -> Directory tree , stores children of a node and its content structure
Page 3

  2. Files -> Metadata tree stores the files and their partition names
 3. Store -> Location where the partitioned file contents are stored
Page 4

  The above 3 cards and their structure is essential for the following commands to run properly.
● mkdir()
Creating a new directory involves first querying the Database for a pre-existing directory. If the directory is new and does not exist, the function proceeds to create the whole directory tree, including and new components.
For eg : /user/umbrella/mercer as an input would create all directories including user, umbrella even if they did not exist. (placeholder acts as an identity file allowing firebase to actually create directory structure. This cannot be done if the card does not have any content)
  Page 5

  Result of mkdir
● ls()
Using the directory structure we first need to modify the input to match our directory structure with ‘/children/’ for each directory giving access to its children.
Once done we can list the contents of any directory.
For empty directories we display a message stating the current directory has no children.
   ● rm()
For rm we have to do a 3 pronged approach and delete the file from 3 places:
a. Dir structure from content list of the path card
b. Files structure to remove the partitions
c. Stores structure to remove the actual partitions
Page 6

 ● put()
Put is one of the more complex implementations, it has the following steps:
1. Split file into given number of partitions:
 2. Insert file into the Dir Structure:
 Page 7

 3. Insert file partition names into the Files Structure:
 4. Insert data into store with partitions:
  Directory Structure after put request
Page 8

  Files Structure after put request
Store Structure after put request
● getPartitionLocations()
We simply access the two Cards Files and Store to get the Partition Locations.
  Page 9

  ● readPartitions()
For reading a numbered partition of the given file, we first ensure that the file exists. Then we use the generated getPartitionLocations() to fetch data from the location.
● cat()
Cat uses the existing function of getPartitionLocations and readPartitions to reconstruct the complete file and return it.
  Page 10

  B.3 Application User Interface Implementation
For the application’s user interface, we used Python3, HTML5/CSS3, Javascript, JQuery, Bootstrap libraries, Axios, and the application uses the Flask web framework as a local development server.
The file structure for the project follows the same structure as specified in the Flask documentation. The Flask web application project structure is as follows:
Flask Project Structure
 Page 11

 The static folder contains the static items that are served by the server. The firebase.js and mysql.js files contain the Javascript, JQuery implementations that render and update the HTML based on the API responses. The styles.css provides the CSS styling template for the project. The templates folder contains index.html, firebase.html, mysql.html, and explanation.html code for front-end. The app.py file creates the Flask application instance as it imports the Flask objects and registers all the front-end paths. The firebase_api.py and mysql_api.py files are the backend code of the application, and they have the REST APIs for each feature implementation.
To start the Flask application instance the following commands are required to be executed on the command line:
The application can be accessed on URL : http://127.0.0.0.1:5432
The URL takes the users to the Project Home page which contains two buttons, which allows users to click on the specific EDFS implementation.
The Home page also contains a ‘About Operations’ button which redirects the user to the explanation page. The explanation page gives the list of features provided by the application.
     Project Home Page
Explanation Page
Page 12

 By clicking on the Firebase or MySQL button on the Project Home page, the user can go to one of the implementations.
Firebase Operations Page MySQL Operations Page
● mkdir()
mkdir on the front-end is given by the ‘New Folder’ button and by clicking on it, an input field appears where the path of the new directory to be created is specified. After that by clicking on the ‘Create’ button, the directory is created. The button click internally calls the Firebase (or MySQL) /mkdir REST API which takes ‘path’ as a parameter, backend processes the request and the API response in JSON format is parsed and rendered on the interface.
    Mkdir directory path entry
Directory created successfully
Page 13

 ● ls()
The ls command can be executed by checking in the File explorer section, by entering the file system path for which the user wants to check the contents for. By clicking on the search icon, the contents of the file are displayed in the section below. If the directory is present, ‘This directory is empty’ message is displayed.
Empty Directory Directory contents displayed
● rm()
The rm command can be executed using the ‘Delete’ button in the FIle Explorer section of the interface. The parameter the /rm API accepts is the filepath. By clicking on the Delete button, if the delete file operation is successful, the alert box is displayed. After deleting the file, check if the file is deleted by using the ls command.
    File deleted successfully
Verifying by using ls command
Page 14

 ● put()
The put command can be used by the user by clicking on the ‘Upload’ button. The number of partitions, file path, and selecting a file from the local system to post the contents is performed by clicking on Upload. Once the upload is successful, alert message is displayed.
Upload file from local Upload done successfully
Uploaded file checked using ls command
   Page 15

● cat()
cat command can be executed by the user by clicking on the ‘Open’ button present. The output of the cat command is displayed in the ‘FILE CONTENT’ tab below.
 cat command output
● getPartitionLocations() and readPartition()
The output for these two commands can be viewed by the user in the ‘Information’ tab. To view the contents of a particular partition, enter the partition number and click on the search icon. The contents of the partition would be displayed below in tabular format.
  getPartitionLocation() output readPartition() output
The search and analysis interface implementation details are present in section C. Both MySQL and Firebase pages have ‘?’ symbols on top for users to access the Explanation Page.
