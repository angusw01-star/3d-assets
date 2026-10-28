// 寶物取得頁的 GAS 範本。
// 用法：在 Apps Script 專案新增 HTML 檔「Index」貼上 Index.html，Code.gs 貼上本檔，部署成網頁應用程式。
function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('寶物：寶劍')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

// 取得寶物時由網頁呼叫。目前只記錄在執行紀錄；要存進試算表或背包，在這裡加程式。
function saveTreasure(name) {
  console.log('取得寶物：' + name + '，使用者：' + Session.getActiveUser().getEmail());
  return true;
}
