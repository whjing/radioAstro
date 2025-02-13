#%%
import pandas as pd

# ========== Step 1: 读取数据 ==========
file_snr = "../cat/SNRcat20250115-SNR.csv"
file_green = "../cat/greencat.csv"
file_obs = "../cat/SNRcat20250115-OBS.csv"

df_snr = pd.read_csv(file_snr, sep=";", comment="#", header=1)
df_green = pd.read_csv(file_green)

# ========== Step 2: 规范化 Green 目录中的 G 名称 ==========
def normalize_g_name(g_name):
    """ 规范化 G 名称（填充数字到固定长度）"""
    parts = g_name[1:].split("+") if "+" in g_name else g_name[1:].split("-")
    l_part = parts[0].zfill(5)  # 填充到5位
    b_part = parts[1].zfill(4)
    return f"G{l_part}{'+' if '+' in g_name else '-'}{b_part}"

df_green["normalized_name"] = df_green["name"].apply(normalize_g_name)

# ========== Step 3: 合并两个数据表 ==========
df_snr["source_from"] = "snrcat"
df_green["source_from"] = "green"

df_snr["normalized_name"] = df_snr["G"]  # 直接使用 G 作为标准化名称

df_merged = pd.merge(df_snr, df_green, on="normalized_name", how="outer")
print(df_merged.columns)


# 筛选表格，保留列Type_X含composite的或Type_Y含C的
df_merged = df_merged[(df_merged["type_x"].str.contains("plerionic composite", na=False)) | (df_merged["type_y"].str.contains("C", na=False))]
# 计数，并打印出来
print(f"筛选后共有 {len(df_merged)} 个源")
# 删除type_x列只有thermal composite的行
df_merged = df_merged[~df_merged["type_x"].str.contains("thermal composite", na=False)]
# 计数，并打印出来
print(f"删除thermal composite后共有 {len(df_merged)} 个源")


# 加一列type_uncertain_green，只要有Type_Y中含?，就type_uncertain_green改为1
df_merged["type_uncertain_green"] = df_merged["type_y"].str.contains("\?", na=False)
df_merged["type_uncertain_green"] = df_merged["type_uncertain_green"].fillna(False)
df_merged["type_uncertain_green"] = df_merged["type_uncertain_green"].astype(int)



# ========== Step 4: 读取观测数据，匹配波段信息 ==========
df_obs = pd.read_csv(file_obs, delimiter=";", skiprows=2)

# 处理 source 列，标记 shell 和 pwn
df_obs["shell"] = df_obs["source"].str.contains("shell", case=False, na=False)
df_obs["pwn"] = df_obs["source"].str.contains("pwn", case=False, na=False)



# **新步骤**：在 groupby 之前创建 `source_flag`
df_obs["source_flag"] = df_obs.apply(
    lambda row: "shell & pwn" if row["shell"] and row["pwn"] else 
                "shell" if row["shell"] else 
                "pwn" if row["pwn"] else "", axis=1
)

# 标记不同波段，如果 df_obs angular_resolution 为(missed)，则认为是false
df_obs["Xray"] = df_obs["energy_domain"].eq("X") & ~df_obs["angular_resolution"].eq("(missed)")
df_obs["gamma_TeV"] = df_obs["energy_domain"].eq("gamma_TeV") & ~df_obs["angular_resolution"].eq("(missed)")
df_obs["gamma_GeV"] = df_obs["energy_domain"].eq("gamma_GeV") & ~df_obs["angular_resolution"].eq("(missed)")

# 如果Xray为true, 则将source_flag信息写入Xray列
df_obs["Xray"] = df_obs.apply(lambda row: row["source_flag"] if row["Xray"] else "", axis=1)
# 如果gamma_TeV为true, 则将source_flag信息写入gamma_TeV列
df_obs["gamma_TeV"] = df_obs.apply(lambda row: row["source_flag"] if row["gamma_TeV"] else "", axis=1)
# 如果gamma_GeV为true, 则将source_flag信息写入gamma_GeV列
df_obs["gamma_GeV"] = df_obs.apply(lambda row: row["source_flag"] if row["gamma_GeV"] else "", axis=1)

print(df_obs["Xray"])



# 添加列 info，用于后续合并
df_obs["info"] = df_obs["source_flag"] + df_obs["energy_domain"]

# xray是xray
agg_obs = df_obs.groupby("SNR_id").agg(
    Xray=("Xray", lambda x: "|".join(x)),
    gamma_TeV=("gamma_TeV", lambda x: "|".join(x)),
    gamma_GeV=("gamma_GeV", lambda x: "|".join(x)),
    source_flag=("source_flag", lambda x: "|".join(x)),
    info=("info", lambda x: "|".join(x)),
).reset_index()



# ========== Step 5: 将波段信息合并到 df_merged ==========
df_final = df_merged.merge(agg_obs, left_on="normalized_name", right_on="SNR_id", how="left")

# ========== Step 6: 处理缺失值 ==========
for col in ["Xray", "gamma_TeV", "gamma_GeV"]:
    df_final[col] = df_final[col].fillna("Nan")

# 默认所有源都有 radio 观测
df_final["radio"] = "yes"

# ========== Step 7: 保存最终合并结果 ==========
output_file_path = "../cat/three-cat.csv"
df_final.to_csv(output_file_path, index=False)

print(f"合并完成，新文件已保存为 {output_file_path}")
# %%
