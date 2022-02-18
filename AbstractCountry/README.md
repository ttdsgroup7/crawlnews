#Abstraction Generator and Country Generator

##1. Abstraction Generator
###Introduction
Automatically extract the content and generate the abstract using Transformers with Bart
###Dependencies
1. Use commands to install dependencies: pip install -r requirements-abstraction.txt

2. We need pre-trained model from Bart, and have two ways to download.
1). git clone and store on the customized location
#####Run the Following command:
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs
git lfs install
git clone https://huggingface.co/sshleifer/distilbart-cnn-12-6
#####Then we can modify the model_name like this:
model_name = "./distilbart-cnn-12-6"

2). Download and store at the specific location
just modify the model_name to the below, and will automatically download when running :
model_name = "sshleifer/distilbart-cnn-12-6"
#####Note: If using this way on Colab or similar, it will need to be downloaded every time.
###Usage
python abstraction_generation.py
##2. Country Generator
###Introduction
Automatically extract the country name from the content
###Dependencies
Use commands to install dependencies: pip install -r requirements-nation.txt
#####Note: Sometimes geograpy may return the error like no such table. If so, download locations.db and move to $HOME/.geograpy (or to "C:\Users\Name\.geograpy3") 
#####links:https://github.com/somnathrakshit/geograpy3/wiki/data/locations.db.gz
###Usage
python nation_name_generator.py
#####Can add one argument to indicate the start id, like:
python nation_name_generator.py 1000