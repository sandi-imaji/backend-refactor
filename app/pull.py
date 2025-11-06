from typing import Union,List
import json,requests as req,pandas as pd,numpy as np,time,urllib3,warnings
from urllib3.exceptions import HTTPError
from app.config import Config
from app.helpers import encode_to_dt_sl
from datetime import datetime,timedelta
from app.logger import Logger

warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_realtime(point_id:str,logger=None,max_retries:int=2,retry_delay:float=0.5,timeout:int=5):
  """
  Get realtime value for a data point with automatic retry on timeout and connection errors.
  
  Args:
    point_id: The identifier for the data point
    logger: Logger instance for logging
    max_retries: Maximum number of retry attempts (default: 3)
    retry_delay: Delay between retries in seconds (default: 1.0)
    timeout: Request timeout in seconds (default: 3)
    
  Returns:
    Current value as float
  """
  url = f"{Config.url}/data_point"
  data = dict(token = Config.token, point_id = point_id)
  last_exception = None

  for attempt in range(max_retries):
    try:
      if logger and attempt > 0: logger.info(f"Retry attempt {attempt + 1}/{max_retries} for point_id {point_id}")
      result = req.post(url, data=data, verify=False, timeout=timeout)
      if result.status_code != 200:
        error_msg = f"status_code: {result.status_code} | text: {result.text} | url: {url}"
        if logger: logger.error(error_msg)
        raise ValueError(error_msg)
      result_json = result.json()
      
      if not result_json:
        error_msg = f"Get Realtime ({point_id}) returned None"
        if logger: logger.error(error_msg)
        raise ValueError(error_msg)
      
      currvalue = result_json.get('currvalue', None)
      
      if currvalue is None:
        error_msg = f"Get Realtime ({point_id}) - 'currvalue' field is missing or None"
        if logger: logger.error(error_msg)
        raise ValueError(error_msg)
      
      if logger: logger.info(f"Point: {point_id} | Successfully retrieved value: {currvalue}")
      
      return float(currvalue)
    
    except (req.exceptions.Timeout, req.exceptions.ConnectionError, HTTPError) as e:
      last_exception = e
      error_type = type(e).__name__
      
      if logger:
        logger.warning(
          f"{error_type} for point_id {point_id} "
          f"(attempt {attempt + 1}/{max_retries}): {str(e)}"
        )
      
      # If this is not the last attempt, wait before retrying
      if attempt < max_retries - 1: time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
      else:
        error_msg = (
          f"Failed after {max_retries} attempts for point_id {point_id}: "
          f"{error_type} - {str(e)}"
        )
        if logger: logger.error(error_msg)
        raise ValueError(error_msg)
    
    except req.exceptions.RequestException as e:
      # For other request exceptions, don't retry
      error_msg = f"Request failed for point_id {point_id}: {str(e)}"
      if logger: logger.error(error_msg)
      raise ValueError(error_msg)
    
    except ValueError as e: raise e
    
    except Exception as e:
      # For non-request exceptions, don't retry
      error_msg = f"Error processing data for point_id {point_id}: {str(e)}"
      if logger: logger.error(error_msg)
      raise ValueError(error_msg)

  # This should not be reached, but just in case
  if last_exception: raise ValueError(f"Failed after {max_retries} attempts: {str(last_exception)}")


def get_history(row_id:int,
                current_date:str,
                time_start:str = "00:00:00",
                time_end:str = "23:59:00",
                interval:int = 5,
                to_dataframe:bool = False,
                logger = None,
                max_retries:int = 3,
                retry_delay: float = 0.7,
                timeout : int = 3):
  """
  Retrieve historical data with automatic retry on timeout and connection errors.
  
  Args:
    row_id: The identifier for the data row
    current_date: Date string in format YYYYMMDD
    time_start: Start time in HH:MM:SS format
    time_end: End time in HH:MM:SS format
    interval: Time interval in seconds
    to_dataframe: Whether to return as DataFrame or list
    logger: Logger instance for logging
    max_retries: Maximum number of retry attempts (default: 3)
    retry_delay: Delay between retries in seconds (default: 1.0)
    timeout: Request timeout in seconds (default: 30)
    
  Returns:
    List of [datetime, values] or DataFrame with datetime index
  """
  headers = {"Content-Type": "application/x-www-form-urlencoded"}
  packet = {
    "function": "getDBHistory",
    "key": Config.key,
    "params": {
      "row_id": int(row_id),
      "current_date": current_date,
      "time_start": time_start,
      "time_end": time_end,
      "interval": interval,
      "quality": 0,
    }
  }
  url = f"{Config.url}/tags/get-history"
  packet = json.dumps(packet)
  payload = {"packet": packet}
  last_exception = None
  for attempt in range(max_retries):
    try:
      if logger and attempt > 0:
        logger.info(f"Retry attempt {attempt + 1}/{max_retries} for row_id {row_id}, date {current_date}")
      
      result = req.post(url, data=payload, headers=headers, verify=False, timeout=timeout)
      
      if result.status_code != 200:
        error_msg = f"status_code is {result.status_code} | url: {url} | text: {result.text}"
        if logger:
          logger.error(error_msg)
        raise ValueError(error_msg)
      
      result_json = result.json()
      
      if not result_json:
        if logger: logger.warning(f"Column: {row_id} | {encode_to_dt_sl(current_date)} | No data returned")
        return pd.DataFrame(columns=["dt", row_id]).set_index("dt") if to_dataframe else [[], []]
      
      if logger:
        logger.info(f"Column: {row_id} | {encode_to_dt_sl(current_date)} | Successfully retrieved!")
      
      # Unpack timestamps and values
      dt, val = zip(*result_json)
      dt = [datetime.fromtimestamp(i/1000,tz=Config.utc) for i in dt]
      
      if to_dataframe:
        df = pd.DataFrame({"dt": dt, row_id: val})
        df["dt"] = pd.to_datetime(df["dt"])
        return df.set_index("dt")
      
      return [dt, val]
    
    except (req.exceptions.Timeout, req.exceptions.ConnectionError, HTTPError) as e:
      last_exception = e
      error_type = type(e).__name__
      
      if logger:
        logger.warning(
          f"{error_type} for row_id {row_id}, date {current_date} "
          f"(attempt {attempt + 1}/{max_retries}): {str(e)}"
        )
      # If this is not the last attempt, wait before retrying
      if attempt < max_retries - 1:
        time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
      else:
        error_msg = (
          f"Failed after {max_retries} attempts for row_id {row_id}: "
          f"{error_type} - {str(e)}"
        )
        if logger:
          logger.error(error_msg)
        raise ValueError(error_msg)
    
    except req.exceptions.RequestException as e:
      # For other request exceptions, don't retry
      error_msg = f"Request failed for row_id {row_id}: {str(e)}"
      if logger:
        logger.error(error_msg)
      raise ValueError(error_msg)
    
    except Exception as e:
      # For non-request exceptions, don't retry
      error_msg = f"Error processing data for row_id {row_id}: {str(e)}"
      if logger:
        logger.error(error_msg)
      raise ValueError(error_msg)
  
  # This should not be reached, but just in case
  if last_exception: raise ValueError(f"Failed after {max_retries} attempts: {str(last_exception)}")

def pulling(dataset_name:str):
  from app.database.db import get_session
  from app.database.orm import Dataset
  from app.database.schemas import StatusProcess,MetaDataset

  logger = Logger(dataset_name)
  logger.info(f"Start Pulling ... {dataset_name}")

  db = next(get_session())
  dataset = Dataset.get_by_name(dataset_name,db)
  if not dataset: raise ValueError(f"{dataset_name} not found!")
  try:
    dataset.status = StatusProcess.RUNNING_PULL
    db.commit()

    if not dataset.task_type.is_dummies():
      columns = dataset.features
      if dataset.task_type.is_supervised(): columns += [dataset.target]

      df = pull_real_data(columns,start_date=dataset.start_date,
                          end_date=dataset.end_date,time_start=dataset.time_start,time_end=dataset.time_end)

    else:
      raise NotImplementedError()
      # df = _generate_dummy_data(dataset, logger)

    if df is None or df.empty: raise ValueError("Generated dataframe is empty")

    df["dt"] = pd.to_datetime(df["dt"])

    dataset.meta = MetaDataset(
      created_at = datetime.now().isoformat(),
      created_by = "Anonymous",
      size_of = df.memory_usage().sum(),
      n_rows = len(df),
      n_cols = len(df.columns),
      missing_values=df.isna().sum().sum().item(),
      is_outlier = False, random_seed = 4,
      columns = df.columns.tolist(),notes = "", train_size = 0.8,
      path = f"storages/{dataset.name}/data.csv"
    )

    df = df.ffill()
    interval = df["dt"].diff().median()  # Gunakan median untuk lebih robust
    dataset.is_valid = True
    dataset.status = StatusProcess.SUCCESS_PULL
    dataset.interval = int(interval.total_seconds() / 60) if isinstance(interval,timedelta) else 0

    logger.info("End Pulling ...")
    db.commit()
    logger.info("Pulled successfully!")


  except Exception as e:
    logger.error(f"Dataset: {dataset_name} | Error: {str(e)}")
    dataset.is_valid = False
    dataset.status = StatusProcess.ERROR_PULL
    db.commit()
    raise

def pull_real_data(columns:List[str],start_date:str,end_date:str,time_start:str,time_end:str,logger=None) -> pd.DataFrame:
  # Parse and validate dates
  fmt = "%Y%m%d"
  try:
    start_date_dt = datetime.strptime(start_date, fmt)
    end_date_dt = datetime.strptime(end_date, fmt)
  except ValueError as e: raise ValueError(f"Invalid date format. Expected YYYYMMDD: {str(e)}")
  
  if start_date_dt > end_date_dt: raise ValueError("Start date cannot be after end date")
  
  # Generate date range
  delta_days = (end_date_dt - start_date_dt).days
  dates = [(start_date_dt + timedelta(days=i)).strftime(fmt) for i in range(delta_days + 1)]
  
  if logger: logger.info(f"Pulling data from {start_date} to {end_date} ({len(dates)} days)")
  
  # Pull data for each feature/target
  results = []
  for col in columns:
    if logger:logger.info(f"Pulling feature: {col}")
    feature_data = []
    
    for date in dates:
      try:
        df_day = get_history(
            int(col),
            date,
            time_start,
            time_end,
            interval=1,
            to_dataframe=True,
            logger=logger
        )
        feature_data.append(df_day)
      except Exception as e:
        if logger:logger.warning(f"Failed to get data for {col} on {date}: {str(e)}")
        continue
    
    if not feature_data: raise ValueError(f"No data retrieved for feature: {col}")
    
    # Concatenate all days for this feature
    feature_df = pd.concat(feature_data, axis=0)
    results.append(feature_df)
  
  # Combine all features
  df = pd.concat(results, axis=1).sort_index()
  
  # Forward fill missing values
  df = df.ffill()
  
  # Reset index and add datetime column
  df["dt"] = df.index
  df.reset_index(drop=True, inplace=True)
  
  return df

def generate_dummy():pass

if __name__ == "__main__":
  columns = ["216998630", "216998631", "216998632", "216998633", "216998634", "216998635"]
  df = pull_real_data(columns,start_date="20250910",end_date="20250911",time_start="00:00:00",time_end="23:59:00")
  interval = df["dt"].diff().median()  # Gunakan median untuk lebih robust

  logger = Logger("test")
  print()


