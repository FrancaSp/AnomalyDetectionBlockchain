from tensorflow.keras.models import load_model
wdir = ''

model = load_model(wdir+'/AutoencoderETCslidMinVarmax100Epoch25May2021091859.h5'
                  , compile = False)
# Save weights and architecture
model.save_weights("AutoencoderETCslidMinVarmax100Epoch25May2021091859weights_only.h5")

# Save model config
json_config = model.to_json()
with open('AutoencoderETCslidMinVarmax100Epoch25May2021091859model_config.json', 'w') as json_file:
    json_file.write(json_config)

model = load_model(wdir+'/AutoencoderETCslidMinVarmedium100Epoch25May2021091856.h5'
                  , compile = False)
# Save weights and architecture
model.save_weights("AutoencoderETCslidMinVarmedium100Epoch25May2021091856weights_only.h5")

# Save model config
json_config = model.to_json()
with open('AutoencoderETCslidMinVarmedium100Epoch25May2021091856model_config.json', 'w') as json_file:
    json_file.write(json_config)

model = load_model(wdir+'/AutoencoderETCslidMinVarmin100Epoch25May2021091859.h5'
                  , compile = False)
# Save weights and architecture
model.save_weights("AutoencoderETCslidMinVarmin100Epoch25May2021091859weights_only.h5")

# Save model config
json_config = model.to_json()
with open('AutoencoderETCslidMinVarmin100Epoch25May2021091859model_config.json', 'w') as json_file:
    json_file.write(json_config)