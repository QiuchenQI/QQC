import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.io as pio
import os
from concurrent.futures import ThreadPoolExecutor

# Parse .asc file and extract timestamps and specified bits of SRSBackboneSignalIPdu02 signal
def parse_asc_file(file):
    data = []
    try:
        for line in file:
            line = line.decode("utf-8")
            if "SRSBackboneSignalIPdu02" in line:
                parts = line.strip().split()
                timestamp = float(parts[0])
                bit_16 = int(parts[18], 16)  
                bit_39 = int(parts[20], 16)  
                bit_25 = int(parts[19], 16)  
                bit_26 = int(parts[19], 16)  
                bit_24 = int(parts[19], 16)  
                bit_28 = int(parts[19], 16)  
                data.append((timestamp, bit_16, bit_39, bit_25, bit_26, bit_24, bit_28))
    except Exception as e:
        st.error(f"Error parsing file: {e}")
    return data

# Convert data to DataFrame
def convert_to_dataframe(data):
    df = pd.DataFrame(data, columns=["Timestamp", "RecOfImpctCrashFrnt", "RecOfImpctCrashRe", "RecOfImpctCrashSideLe", "RecOfImpctCrashSideRi", "RecOfImpctCrashRollovr", "RecOfImpctCrashState"])
    return df

# Calculate duration of value changes
def calculate_duration(df, column):
    df['Change'] = df[column].diff().fillna(0).astype(bool)
    change_indices = df[df['Change']].index
    durations = []
    for i in range(len(change_indices) - 1):
        start_idx = change_indices[i]
        end_idx = change_indices[i + 1]
        duration = df.loc[end_idx, 'Timestamp'] - df.loc[start_idx, 'Timestamp']
        durations.append((df.loc[start_idx, 'Timestamp'], df.loc[start_idx, column], duration))
    return pd.DataFrame(durations, columns=['Timestamp', column, 'Duration'])

def upload_files():
    return st.file_uploader("Upload ASC files", accept_multiple_files=True, type=["asc"])

def process_file(file, colors, color_index):
    data = parse_asc_file(file)
    if not data:
        return None, None
    
    df = convert_to_dataframe(data)
    
    # Create a directory for the current ASC file
    report_dir = os.path.join("C:\\reports", os.path.splitext(file.name)[0])
    os.makedirs(report_dir, exist_ok=True)
    
    # Plot interactive charts and display duration of value changes
    column_titles = {
        "RecOfImpctCrashFrnt": "RecOfImpctCrashFrnt",  # bit16
        "RecOfImpctCrashRe": "RecOfImpctCrashRe",      # bit39
        "RecOfImpctCrashSideLe": "RecOfImpctCrashSideLe",  # bit25
        "RecOfImpctCrashSideRi": "RecOfImpctCrashSideRi",  # bit26
        "RecOfImpctCrashRollovr": "RecOfImpctCrashRollovr",  # bit24
        "RecOfImpctCrashState": "RecOfImpctCrashState"  # bit28
    }
    
    durations_summary = {}
    
    for column, title in column_titles.items():
        duration_df = calculate_duration(df, column)
        fig = px.line(df, x="Timestamp", y=column, title=f"{title} Data for {file.name}", labels={"Timestamp": "Timestamp", column: "Value"}, color_discrete_sequence=[colors[color_index % len(colors)]])
        for _, row in duration_df.iterrows():
            fig.add_annotation(x=row['Timestamp'], y=df.loc[df['Timestamp'] == row['Timestamp'], column].values[0], text=f"Duration: {row['Duration']:.2f}s", showarrow=True, arrowhead=1)
        
        # Check duration and add PASS/FAIL annotation
        max_duration = duration_df['Duration'].max()
        if max_duration > 3.8:
            fig.add_annotation(text="PASS", xref="paper", yref="paper", x=0.95, y=0.95, showarrow=False, font=dict(color="green", size=20))
        elif 0 < max_duration <= 3.8:
            fig.add_annotation(text="FAIL", xref="paper", yref="paper", x=0.95, y=0.95, showarrow=False, font=dict(color="red", size=20))
        
        # Save the figure to the report directory
        fig_path = os.path.join(report_dir, f"{title}.png")
        pio.write_image(fig, fig_path, width=800, height=600)
        
        # Summarize durations
        if not duration_df.empty:
            durations_summary[title] = duration_df['Duration'].sum()
        else:
            durations_summary[title] = "no change"
    
    return file.name, durations_summary

def main():
    st.set_page_config(page_title="CANoe Trace Data Analysis", layout="wide")
    st.title("CANoe Trace Data Analysis")
    
    files = upload_files()
    
    if files:
        st.success("Files have been uploaded successfully!")
        colors = px.colors.qualitative.Plotly  # Use Plotly's qualitative color scale
        color_index = 0
        
        all_durations_summary = {}
        
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_file, file, colors, color_index + i) for i, file in enumerate(files)]
            for future in futures:
                try:
                    file_name, durations_summary = future.result()
                    if file_name and durations_summary:
                        all_durations_summary[file_name] = durations_summary
                except Exception as e:
                    st.error(f"Error processing file: {e}")
        
        # Display durations summary at the bottom of the page
        st.subheader("Duration Summary for All Files")
        for file_name, durations_summary in all_durations_summary.items():
            st.write(f"**{file_name}**")
            for title, duration in durations_summary.items():
                st.write(f"{title}: {duration}")

if __name__ == "__main__":
    main()