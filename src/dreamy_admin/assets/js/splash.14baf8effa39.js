/** @type {import('gsap').gsap} */
const gsap = window.gsap;


        document.addEventListener("DOMContentLoaded", (event) => {


            const logo = document.querySelector("#dreamy");
            const brandWrapper = document.querySelector("#brand-wrapper");
            const brandLink = document.querySelector("#brand-link");
            const paths = logo.querySelectorAll("path");


        const tl = gsap.timeline({
        });
            tl.set(brandWrapper,{
            position:"fixed",
                top:0,
                left:0,
                width:"100vw",
                height:"100vh",
                zIndex: 9999,
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: "var(--bs-secondary)"
            });

            tl.set(brandLink,{
                disabled:'true'
            })
            tl.set(logo,{
                top:"50%",
                left:"50%",
                width:"100vw",
                height:"100vh",
                fill:"var(--bs-secondary)",
                zIndex: 9999,
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: "var(--bs-secondary)"

            });

            tl.set(paths,{
                stroke:"var(--bs-primary)",
                strokeWidth:3,
                fill:"var(--bs-secondary)",
            })

            tl.addLabel("colorOne",.6);
            tl.addLabel("colorTwo",1);
            tl.addLabel("colorThree",1.4);
            tl.addLabel("backHome",1.8);
            tl.addLabel("settle",2.2);

            // first
            tl.to(
                logo,{
                    backgroundColor:"var(--bs-primary)",
                    duration:.1,
                },
                "colorOne");

            tl.to(
                paths,{
                    fill:"var(--bs-primary)",
                    stroke:"var(--bs-secondary)",
                    duration:.1,
                },
                "colorOne");


            // second
            tl.to(
                logo,{
                    backgroundColor:"var(--bs-secondary)",
                    duration:.1,
                },"colorTwo");

            tl.to(
                paths,{
                    fill:"var(--bs-primary)",
                    duration:.1,
                },"colorTwo");

            //three
            tl.to(
                logo,{
                    backgroundColor:"var(--bs-primary)",
                    duration:.1,
                },"colorThree");

            tl.to(
                paths,{
                    fill:"var(--bs-secondary)",
                    duration:.1,
                },"colorThree");


            // back home
            tl.to(logo,{
                height:"2rem",
                duration:.2,
            },"backHome")
            tl.to(brandWrapper,{
                height:"3.7rem",
                duration:.2,

            },"backHome")

            tl.to(logo,{
                width:"2rem",
                duration:.2,
                opacity:.15,
                y:0,
                x:0

            },"backHome +=.2")
            tl.to(brandWrapper,{
                width:"8rem",
                duration:.2,
                opacity:.15,
                y:-5,
                x:15
            },"backHome +=.2")


            //settle
            tl.to(logo,{
                clearProps:"all",
                duration:.3,
                opacity:1

            },"settle")
            tl.to(brandWrapper,{
                clearProps:"all",
                duration:.3,
                opacity:1
            },"settle")
        })


