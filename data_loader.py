import mne
import pandas as pd
import numpy as np
import os

class EEGLoader:        #dosya yükleme ve veriye ulaşma
    def __init__(self,file_path):       
        self.file_path = file_path
        self.raw = None      
        self.raw_data = None            
        self.sampling_rate= None        
        self.channel_names = None

    #Dosya Formatına Göre Yükleme

    def load_edf(self):#EDF ve BDF dosyalarının yüklenmesi
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"{self.file_path} bulunamadı!")
        self.raw = mne.io.read_raw_edf(self.file_path, preload=True)
        self.channel_names = self.raw.ch_names
        print("EDF CHANNEL NAMES:", self.channel_names)
        self.raw_data = self.raw.get_data() #(channels x samples)
        self.sampling_rate = int(self.raw.info['sfreq'])
        self.channel_names = self.raw.info.ch_names

    def load_csv(self):#CSV dosyalarının yüklenmesi
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"{self.file_path} bulunamadı!")
        df = pd.read_csv(self.file_path)
        self.raw_data = df.to_numpy().T #Transpoz: kanallar x örnekler
        self.sampling_rate = 250 #varsayılan 250 Hz fakat csv dosyası ile kullanıcı da verebilir
        self.channel_names = list(df.columns)

    def load_mat(self):
        from scipy.io import loadmat
        import numpy as np
        import os

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"{self.file_path} bulunamadı!")

        mat = loadmat(self.file_path, squeeze_me=True, struct_as_record=False)

        print("MAT KEYS:", mat.keys())

        def find_2d_array(obj, depth=0, max_depth=6):
            if depth > max_depth:
                return None

            if isinstance(obj, np.ndarray):
                if obj.ndim == 2 and obj.shape[0] > 1 and obj.shape[1] > 1:
                    return obj

                # object array ise içini dolaş
                if obj.dtype == object:
                    flat = obj.flatten()
                    for item in flat:
                        found = find_2d_array(item, depth + 1, max_depth)
                        if found is not None:
                            return found

            # matlab struct benzeri nesneler
            if hasattr(obj, "__dict__"):
                for key, value in obj.__dict__.items():
                    found = find_2d_array(value, depth + 1, max_depth)
                    if found is not None:
                        return found

            # dict ise içini dolaş
            if isinstance(obj, dict):
                for key, value in obj.items():
                    found = find_2d_array(value, depth + 1, max_depth)
                    if found is not None:
                        return found

            return None

        candidate_keys = [k for k in mat.keys() if not k.startswith("__")]

        selected_data = None
        selected_key = None

        for key in candidate_keys:
            value = mat[key]
            print(f"CHECKING KEY: {key}, TYPE: {type(value)}, SHAPE: {getattr(value, 'shape', None)}")

            found = find_2d_array(value)
            if found is not None:
                selected_data = np.array(found)
                selected_key = key
                break

        if selected_data is None:
            raise ValueError(f"Uygun 2 boyutlu EEG matrisi bulunamadı. Keyler: {candidate_keys}")

        print("SELECTED MAT KEY:", selected_key)
        print("RAW DATA SHAPE BEFORE FORMAT:", selected_data.shape)

        self.raw_data = np.array(selected_data)

        print("MAT SELECTED OBJECT ATTRIBUTES:", dir(mat[selected_key]))

        # Kanal isimlerini çekmeye çalış
        self.channel_names = None

        try:
            eeg_obj = mat[selected_key]

            # Olası alan adları
            possible_fields = ["chanlocs", "channels", "channel_names", "labels"]

            for field in possible_fields:
                if hasattr(eeg_obj, field):
                    field_value = getattr(eeg_obj, field)
                    print(f"FOUND CHANNEL FIELD: {field}")
                    print("FIELD TYPE:", type(field_value))

                    extracted_names = []

                    # Eğer liste / numpy array gibi yapıysa
                    if isinstance(field_value, (list, tuple, np.ndarray)):
                        for item in np.ravel(field_value):
                            if hasattr(item, "labels"):
                                xtracted_names.append(str(item.labels))
                            elif hasattr(item, "label"):
                                extracted_names.append(str(item.label))
                            elif isinstance(item, str):
                                extracted_names.append(item)

                    # Eğer doğrudan labels alanı varsa
                    elif hasattr(field_value, "labels"):
                        extracted_names.append(str(field_value.labels))

                    if extracted_names:
                        self.channel_names = extracted_names
                        break

            if self.channel_names is None:
                self.channel_names = [f"Ch{i+1}" for i in range(self.raw_data.shape[0])]

        except Exception as e:
            print("MAT channel extraction failed:", e)
            self.channel_names = [f"Ch{i+1}" for i in range(self.raw_data.shape[0])]

        print("MAT CHANNEL NAMES:", self.channel_names)

        # Kanal isimlerini çekmeye çalış
        try:
            if hasattr(mat[selected_key], "chanlocs"):
                chanlocs = mat[selected_key].chanlocs

                channel_names = []

                for ch in chanlocs:
                    if hasattr(ch, "labels"):
                        channel_names.append(str(ch.labels))

                if channel_names:
                    self.channel_names = channel_names
                    print("MAT CHANNEL NAMES:", self.channel_names)
                else:
                    self.channel_names = [f"Ch{i+1}" for i in range(self.raw_data.shape[0])]

            else:
                self.channel_names = [f"Ch{i+1}" for i in range(self.raw_data.shape[0])]

        except Exception as e:
            print("MAT channel extraction failed:", e)
            self.channel_names = [f"Ch{i+1}" for i in range(self.raw_data.shape[0])]

        # channels x samples formatına getir
        if self.raw_data.shape[0] > self.raw_data.shape[1]:
            self.raw_data = self.raw_data.T

        sfreq_value = mat.get("sfreq", mat.get("fs", 250))
        try:
            self.sampling_rate = int(np.array(sfreq_value).flatten()[0])
        except:
            self.sampling_rate = 250

        channel_names = mat.get("channel_names")

        if channel_names is not None:
            try:
                self.channel_names = [str(c) for c in channel_names.flatten()]
            except:
                self.channel_names = [f"Ch{i+1}" for i in range(self.raw_data.shape[0])]
        else:
            self.channel_names = [f"Ch{i+1}" for i in range(self.raw_data.shape[0])]


    #standart veri formatı
    def get_standardized_data(self):
        if hasattr(self, "raw") and self.raw is not None:
            return self.raw.get_data()
        elif hasattr(self, "raw_data") and self.raw_data is not None:
            return self.raw_data("float32")
        else:
            raise ValueError("Henüz veri yüklenmedi. Önce uygun load fonksiyonunu çağırın.")

