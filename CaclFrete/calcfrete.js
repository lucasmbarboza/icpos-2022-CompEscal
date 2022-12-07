module.exports = async function (context) {
  console.log(context.request.body);
  let obj = context.request.body;
  return {
    status: 200,
    body: "CALC_FRETE_EXECUTED " + JSON.stringify(obj),
  };
};
