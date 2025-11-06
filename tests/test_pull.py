from app.pull import get_history,get_realtime
import unittest 


class TestPull(unittest.TestCase):
  def setUp(self) -> None:
    self.payload_history = dict(
      row_id = "216998630",
      current_date = "20250910",
    )
    self.payload_realtime = dict(
      point_id = "5b0fe6d50488fbaa219972e272f1c14e",
    )
  def test_get_history(self):
    data = get_history(row_id="216998630",current_date="20250910",to_dataframe=True)
    print(data)


if __name__ == "__main__":
  unittest.main()


