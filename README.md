# NUEVOLENS
### A project that combines facial recognition with homomorphic encryption to achieve secured surveillance

# Introduction
- Has two streams running in parallel; HE stream is stream 1, AES is stream 2
- Project is divided into 3 modules; edge node 1, server node 2, admin node 3
- Edge node accesses video feed of webcam
- module 1_1 Collects face data, encrypts with HE public_context.tenseal and sends to module 2.1
- module 1_2 encrypts frames through 256-bit AES and sends to module 2.2
- module 2.1 processes and sends encrypted data to module 3.1
- module 2.2 saves the incoming encrypted frames as 10 second encrypted videos in hourly folders
- module 3 decrypts the data, generates suitable logs and notifications
- module 3.2 can search and decrypt AES encrypted videos
- add_identity.py is used to generate encrypted embeddings pickle file to be used for comparison
- context_generator is used to generate public and private HE keys
- decrypt_he_emb is used to decrypt and plot encrypted embeddings stored at runtime


# Installation & Execution
1. Set interpreter of your environment to python 3.9. python 3.10 and later are incompatible with tenseal (our homomorphic encryption library)
   
2. Install requirements
```sh
$ pip install -r requirements.txt
```

3. Set the IP addresses and file_path dependencies in respective python files

4. Face Recognition model InceptionResnet with VGGFACE2 is a 109 MB file stored at [torch folder in Drive](https://drive.google.com/drive/folders/1jlIk2Z7BkRWWmF8duRDkaWMWesLRGGkK?usp=sharing "Go to Google Drive"). Download the *torch* folder

5. It must contain *checkpoints* folder which must contain a *.pt* file of 109 MB

6. Save the *torch* folder to your user account's .cache folder for running add_identity.py and module_1_1.py

7. Run module_3.1
```sh
$ python module_3.1.py
```
8. Then run module_2.1 and module_2.2
```sh
$ python module_2.1.py
$ python module_2.2.py
```
9. Then run nuevolens1.py, it will call 1.1 and 1.2 itself
```sh
$ python nuevolens1.py
```

Made By : [FASH](mailto:fashnuevolens@gmail.com)<br>
**Secured Surveillance, Ooooh Yeah!**
