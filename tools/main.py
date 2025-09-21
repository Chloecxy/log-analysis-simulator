from tools.analyze_logs import *
from tools.enrich_apis import *


def main():
    # Analyze logs
    # parse_log()
    #
    # # Enrich flagged IPs
    # hourly_logs_dataframe = pd.read_csv("csv/hourly_logs_summary.csv")
    # hourly_logs_dataframe['DateTime'] = pd.to_datetime(hourly_logs_dataframe['DateTime'])
    # raw_logs_dataframe = pd.read_csv("csv/raw_log.csv")
    # raw_logs_dataframe['DateTime'] = pd.to_datetime(raw_logs_dataframe['DateTime'])
    #
    # current_date = datetime.strptime("2025 Jul 08", "%Y %b %d").date()
    # current_month_raw_logs_dataframe = raw_logs_dataframe[
    #     raw_logs_dataframe['DateTime'].dt.month == current_date.month]
    #
    # ip_fail_count_df = current_month_raw_logs_dataframe.groupby(["IP"]).agg({'Status': lambda x: (x == "Failed").sum()})
    # ip_fail_count_df.reset_index()
    # ip_fail_count_df.rename(columns={'Status': 'Failed Attempt Count'}, inplace=True)
    # enriched = enrich_ip(ip_fail_count_df.index.tolist())
    # print(f"Enriched {len(enriched)} IPs.")
    # save_csv(enriched, "malicious_ips.csv")

    hourly_logs_dataframe = pd.read_csv("../csv/hourly_logs_summary.csv")
    hourly_logs_dataframe['DateTime'] = pd.to_datetime(hourly_logs_dataframe['DateTime'])
    raw_logs_dataframe = pd.read_csv("../csv/raw_log.csv")
    raw_logs_dataframe['DateTime'] = pd.to_datetime(raw_logs_dataframe['DateTime'])
    malicious_dataframe = pd.read_csv("../csv/malicious_ips.csv")
    malicious_dataframe['ip'] = malicious_dataframe['ip'].astype(str)
    malicious_dataframe.rename(columns={'ip': 'IP'}, inplace=True)

    # Data for ascore_failed_attempts graph
    current_date = datetime.strptime("2025 Jul 08", "%Y %b %d").date()
    current_month_raw_logs_dataframe = raw_logs_dataframe[
        raw_logs_dataframe['DateTime'].dt.month == current_date.month]

    ip_fail_count_df = current_month_raw_logs_dataframe.groupby(["IP"]).agg({'Status': lambda x: (x == "Failed").sum()})
    ip_fail_count_df.reset_index()
    ip_fail_count_df.rename(columns={'Status': 'Failed Attempt Count'}, inplace=True)

      # Data for usage_type_ascore graph
    malicious_dataframe['bin'] = pd.cut(
        malicious_dataframe['abuse_score'],
        bins=range(0, 110, 10),  # 0–100 in steps of 10
        right=False
    )

    hist_data = (
        malicious_dataframe.groupby(['bin', 'usage_type'], observed=False)
        .size()
        .reset_index(name="count")
    )

    nivo_data = []
    for b in hist_data['bin'].cat.categories:
        row = {"bin": str(b)}
        for usage in hist_data['usage_type'].unique():
            val = hist_data[(hist_data['bin'] == b) & (hist_data['usage_type'] == usage)]['count']
            row[usage] = int(val.iloc[0]) if not val.empty else 0
        nivo_data.append(row)

    print(nivo_data)

if __name__ == "__main__":
    main()
