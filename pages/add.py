class RemoveDuplicates(IPreprocessingStrategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if not df.duplicated().any():
            st.warning("This dataset has no duplicates.")
            return df

        @st.dialog("Handle Duplicates")
        def show_duplicate_dialog():
            duplicate_rows = df[df.duplicated()]
            st.write("### Duplicates Found (Highlighted in Green):")
            styled_duplicates = duplicate_rows.style.apply(lambda x: ['background-color: lightgreen' for _ in x], axis=1)
            st.dataframe(styled_duplicates)

            if st.button("Remove Duplicates"):
                df_cleaned = df.drop_duplicates().copy()
                st.success("All the duplicates are removed successfully.")
                st.session_state['df_preprocessed'] = df_cleaned
                st.session_state['duplicates_removed'] = True
                st.session_state['show_before_after_button'] = True
                st.session_state['show_save_button'] = True
                st.session_state['show_duplicates_dialog'] = False

        if 'show_duplicates_dialog' not in st.session_state:
            st.session_state['show_duplicates_dialog'] = True

        if st.session_state['show_duplicates_dialog']:
            show_duplicate_dialog()

        return df if 'df_preprocessed' not in st.session_state else st.session_state['df_preprocessed']

class FillMissingValues(IPreprocessingStrategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if not df.isnull().values.any():
            st.warning("This dataset has no missing values.")
            return df

        missing_columns = df.columns[df.isnull().any()].tolist()
        missing_summary = df.isnull().sum()

        @st.dialog("Handle Missing Values")
        def show_fill_missing_dialog():
            st.write("### Columns with Missing Values:")
            st.dataframe(missing_summary[missing_summary > 0])

            filled_df = df.copy()
            for col in missing_columns:
                col_type = df[col].dtype

                st.write(f"#### How would you like to fill missing values in `{col}`?")

                if col_type in ['int64', 'float64']:
                    fill_option = st.selectbox(f"Fill method for `{col}` (Numerical)", ["Mean", "Median", "Mode", "Constant"],
                                               help="Select how to fill missing numerical values.")
                    if fill_option == "Mean":
                        filled_df[col] = df[col].fillna(df[col].mean())
                    elif fill_option == "Median":
                        filled_df[col] = df[col].fillna(df[col].median())
                    elif fill_option == "Mode":
                        filled_df[col] = df[col].fillna(df[col].mode()[0])
                    elif fill_option == "Constant":
                        constant_value = st.number_input(f"Enter a constant value for `{col}`")
                        filled_df[col] = df[col].fillna(constant_value)

                else:
                    fill_option = st.selectbox(f"Fill method for `{col}` (Categorical)", ["Mode", "Constant"],
                                               help="Select how to fill missing categorical values.")
                    if fill_option == "Mode":
                        filled_df[col] = df[col].fillna(df[col].mode()[0])
                    elif fill_option == "Constant":
                        constant_value = st.text_input(f"Enter a constant value for `{col}`")
                        filled_df[col] = df[col].fillna(constant_value)

            if st.button("Apply Filling"):
                st.success("Missing values have been filled.")
                st.session_state['df_preprocessed'] = filled_df
                st.session_state['missing_values_filled'] = True
                st.session_state['show_before_after_button'] = True
                st.session_state['show_save_button'] = True
                st.session_state['show_fill_missing_dialog'] = False

        if 'show_fill_missing_dialog' not in st.session_state:
            st.session_state['show_fill_missing_dialog'] = True

        if st.session_state['show_fill_missing_dialog']:
            show_fill_missing_dialog()

        return df if 'df_preprocessed' not in st.session_state else st.session_state['df_preprocessed']

# Concrete strategy: Scale Features (Unchanged)
class ScaleFeatures(IPreprocessingStrategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

        if not numerical_columns:
            st.warning("This dataset has no numerical columns to scale.")
            return df

        @st.dialog("Scale Features")
        def show_scale_features_dialog():
            st.write("### Numerical Columns for Scaling:")
            st.write(numerical_columns)

            scale_method = st.selectbox("Select scaling method", ["Standardization (Mean=0, Std=1)",
                                                                  "Normalization (0-1 range)",
                                                                  "Robust Scaling",
                                                                  "MaxAbs Scaling"],
                                        help="Choose the scaling method to apply to the dataset.")

            scaled_df = df.copy()

            if scale_method == "Standardization (Mean=0, Std=1)":
                scaler = StandardScaler()
            elif scale_method == "Normalization (0-1 range)":
                scaler = MinMaxScaler()
            elif scale_method == "Robust Scaling":
                scaler = RobustScaler()
            elif scale_method == "MaxAbs Scaling":
                scaler = MaxAbsScaler()

            scaled_df[numerical_columns] = scaler.fit_transform(df[numerical_columns])

            if st.button("Apply Scaling"):
                st.success("Scaling has been applied.")
                st.session_state['df_preprocessed'] = scaled_df
                st.session_state['scaling_applied'] = True
                st.session_state['show_before_after_button'] = True
                st.session_state['show_save_button'] = True
                st.session_state['show_scale_features_dialog'] = False

        if 'show_scale_features_dialog' not in st.session_state:
            st.session_state['show_scale_features_dialog'] = True

        if st.session_state['show_scale_features_dialog']:
            show_scale_features_dialog()

        return df if 'df_preprocessed' not in st.session_state else st.session_state['df_preprocessed']

# New Concrete strategy: Encode Data (without Target Encoding)
class EncodeData(IPreprocessingStrategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()

        if not categorical_columns:
            st.warning("This dataset has no categorical columns to encode.")
            return df

        @st.dialog("Encode Data")
        def show_encode_dialog():
            st.write("### Categorical Columns for Encoding:")
            st.write(categorical_columns)

            encoding_method = st.selectbox("Select encoding method", ["One-Hot Encoding", "Label Encoding", "Binary Encoding", "Frequency Encoding"],
                                           help="Choose how to encode categorical data.")

            encoded_df = df.copy()

            if encoding_method == "One-Hot Encoding":
                encoded_df = pd.get_dummies(df, columns=categorical_columns)
            elif encoding_method == "Label Encoding":
                label_encoders = {}
                for col in categorical_columns:
                    label_encoders[col] = LabelEncoder()
                    encoded_df[col] = label_encoders[col].fit_transform(df[col])

            elif encoding_method == "Binary Encoding":
                binary_encoder = BinaryEncoder(cols=categorical_columns)
                encoded_df = binary_encoder.fit_transform(df)

            elif encoding_method == "Frequency Encoding":
                for col in categorical_columns:
                    freq_encoding = df[col].value_counts(normalize=True)
                    encoded_df[col] = df[col].map(freq_encoding)

            if st.button("Apply Encoding"):
                st.success(f"{encoding_method} has been applied.")
                st.session_state['df_preprocessed'] = encoded_df
                st.session_state['encoding_applied'] = True
                st.session_state['show_before_after_button'] = True
                st.session_state['show_save_button'] = True
                st.session_state['show_encode_dialog'] = False

        if 'show_encode_dialog' not in st.session_state:
            st.session_state['show_encode_dialog'] = True

        if st.session_state['show_encode_dialog']:
            show_encode_dialog()

        return df if 'df_preprocessed' not in st.session_state else st.session_state['df_preprocessed']