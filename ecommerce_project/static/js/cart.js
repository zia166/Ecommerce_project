var updateBtns = document.getElementsByClassName("update-cart")
for (i=0;i < updateBtns.length;i++){
    console.log("Hello")
    updateBtns[i].addEventListener("click",function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'Action:', action)
        // console.log("productId:",productId,"action:",action)
    })
}