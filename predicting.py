from copy import deepcopy

from extras.generator import generate_mesh
from extras.custom_functions import read_mesh_from_file, read_receivers_from_file, write_mesh_to_file, draw_mesh_ax
from extras.point import Point
from torch_network import inverse_net_predict, Net

from matplotlib import pyplot as plt


def predict_to_files(recv_file, mesh, model, output_path, plot_path):
    receivers = read_receivers_from_file(recv_file)

    result_mesh = deepcopy(mesh)
    result_mesh = inverse_net_predict(receivers, result_mesh, model_path=model)
    write_mesh_to_file(output_path, result_mesh)

    fig, ax = plt.subplots(2, 1)
    # fig = plt.figure(figsize=(8.0, 2.4), constrained_layout=True)
    draw_mesh_ax(ax[0], mesh)
    draw_mesh_ax(ax[1], result_mesh)
    ax[0].set_title("а) Исходная модель")
    ax[1].set_title("б) Результат предсказания")
    fig.tight_layout()

    plt.savefig(plot_path)
    plt.close(fig)


if __name__ == "__main__":
    Nx = 20
    Nz = 10
    start_pnt = Point(0, -50, 0)
    end_pnt = Point(2000, 50, -1000)
    mesh = generate_mesh(start_pnt, end_pnt, count_x=Nx, count_y=1, count_z=Nz)

    model_path = "models/model_100.pkl"
    # # # model_path = "models/model_1000_detail.pkl"
    # dateset_size = 100
    # dataset = "dataset_0"
    # for i in range(dateset_size):
    #     mesh = read_mesh_from_file(f"datasets/{dataset}/mesh_{i}.mes")
    #     predict_to_files(recv_file=f"datasets/{dataset}/receivers_{i}.dat",
    #                      mesh=mesh,
    #                      output_path=f"datasets/results/{dataset}/result_{i}.mes",
    #                      plot_path=f"datasets/results/{dataset}/png/mesh_{i}.png",
    #                      model=model_path)

    # predict_to_files(f"results/receivers_26.dat", mesh, "datasets/test_dataset/result.mes", "datasets/test_dataset/mesh_plot.png")

    dataset = "test_dataset"
    items = ["snake", "2up", "cube", "2cubes", "vertical", "cube_5x_less", "cube_5x_more"]
    for item in items:
        mesh = read_mesh_from_file(f"datasets/{dataset}/{item}.mes")
        predict_to_files(f"datasets/{dataset}/{item}.dat", mesh, model_path, f"datasets/{dataset}/{item}_result.mes", f"datasets/{dataset}/png/{item}_mesh_plot.png")

