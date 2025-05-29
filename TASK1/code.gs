
const SPREADSHEET_ID = SpreadsheetApp.getActiveSpreadsheet().getId();
const SHEET_NAME = "ESP32sensordata"; 
function doGet(e) {
  try {
    
    var temperature = e.parameter.temperature;
    var humidity = e.parameter.humidity;
    var timestamp = new Date();

    if (temperature === undefined || humidity === undefined) {
      return ContentService.createTextOutput(JSON.stringify({ "status": "error", "message": "Missing temperature or humidity parameter" })).setMimeType(ContentService.MimeType.JSON);
    }

    // Get the sheet
    var spreadSheet = SpreadsheetApp.openById(SPREADSHEET_ID);
    var sheet = spreadSheet.getSheetByName(SHEET_NAME);

    if (!sheet) {
      sheet = spreadSheet.insertSheet(SHEET_NAME);
      sheet.appendRow(["Timestamp", "Temperature", "Humidity"]); 
    }

    // Append the new data
    sheet.appendRow([timestamp, temperature, humidity]);

    // Return a success response
    return ContentService.createTextOutput(JSON.stringify({ "status": "success", "message": "Data received", "temperature": temperature, "humidity": humidity })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
   
    Logger.log(error.toString());

    return ContentService.createTextOutput(JSON.stringify({ "status": "error", "message": error.toString() })).setMimeType(ContentService.MimeType.JSON);
  }
}
