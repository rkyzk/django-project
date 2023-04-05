// Confirm if user really wants to delete the comment
const DELETE_COMMENT ="Are you sure you want to delete your comment?"
$('.delete_comment').click(function() {
  return confirm(DELETE_COMMENT);
});

// 「戻る」ボタン押下時の確認ダイアログ
const Previous ="入力内容は保存されません。前画面に戻りますか？"
$('.previous').click(function() {
  if(confirm(Previous)){
    location.href="product-list";
  }
  return false;
});

// 商品情報更新時の確認ダイアログ
const Update ="商品情報を更新しますか？"
$('.update').click(function() {
  return confirm(Update);
});

// 商品情報削除時の確認ダイアログ
const Delete ="商品情報を削除しますか？"
$('.delete').click(function() {
  return confirm(Delete);
});