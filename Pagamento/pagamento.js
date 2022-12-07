module.exports = async function (context) {
  console.log(context.request.body);
  let obj = context.request.body;
  return {
    status: 200,
    body: "PAGAMENTO_EXECUTED " + JSON.stringify(obj),
  };
};
